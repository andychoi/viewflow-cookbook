from django.contrib.auth import get_user_model
from django.utils.functional import classproperty
from rest_framework import serializers
from rest_framework.utils.model_meta import get_field_info
from viewflow.workflow.models import Process, Task
from viewflow.workflow.fields import get_flow_ref, get_task_ref


class FlowClassSerializer(object):
    def __init__(self, context=None):
        self.context = context or {}

    @property
    def flow_class(self):
        return self.context["view"].flow_class

    def get_start_actions(self):
        user = self.context["request"].user
        actions = []
        for node in self.flow_class.instance.get_start_nodes(user):
            actions.append(
                {
                    "name": node.name,
                    "flow_task": get_task_ref(node),
                    "title": node.task_title,
                    "description": node.task_description,
                    "url": node.reverse("start"),
                }
            )
        actions.sort(key=lambda action: action["name"])

        return actions

    @property
    def data(self):
        return {
            "flow_class": get_flow_ref(self.flow_class),
            "title": self.flow_class.process_title,
            "description": self.flow_class.process_description,
            "start_actions": self.get_start_actions(),
        }


class UserSerializer(serializers.ModelSerializer):
    short_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    def get_short_name(self, user):
        return user.get_short_name() if hasattr(user, "get_short_name") else None

    def get_full_name(self, user):
        return user.get_full_name() if hasattr(user, "get_full_name") else None

    class Meta:
        @classproperty
        def model(cls):
            return get_user_model()

        @classproperty
        def fields(cls):
            return tuple(cls.model.REQUIRED_FIELDS) + (
                cls.model._meta.pk.name,
                cls.model.USERNAME_FIELD,
                "short_name",
                "full_name",
            )


class BaseProcessSerializer(serializers.ModelSerializer):
    flow_class = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    brief = serializers.SerializerMethodField()

    class Meta:
        model = Process
        read_only_fields = ["status", "finished"]
        fields = "__all__"

    def get_flow_class(self, process):
        return get_flow_ref(process.flow_class)

    def get_url(self, process):
        # TODO: if no flow_viewset lookup for {request.resolver_match.namespace}.process_detail
        flow_viewset = getattr(
            self.context["request"].resolver_match, "flow_viewset", None
        )
        if flow_viewset:
            return flow_viewset.reverse("process_detail", args=[process.pk])
        return ""

    def get_title(self, process):
        return process.flow_class.process_title

    def get_description(self, process):
        return process.flow_class.process_description

    def get_brief(self, process):
        return process.brief


class ProcessSerializer(BaseProcessSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fields = getattr(kwargs["context"]["view"], "fields")
        if fields is not None:
            allowed, existing = set(fields), set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

            # Virtual fields fro a proxy model
            info = get_field_info(self.Meta.model)
            for field_name in allowed - existing:
                if field_name not in info.fields:
                    info.fields_and_pk[field_name] = info.fields[
                        field_name
                    ] = self.Meta.model._meta.get_field(field_name)
                field_class, field_kwargs = self.build_field(
                    field_name, info, self.Meta.model, 0
                )
                self.fields[field_name] = field_class(**field_kwargs)


class TaskSerializer(serializers.ModelSerializer):
    flow_task = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    brief = serializers.SerializerMethodField()
    process_brief = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()
    owner = UserSerializer(allow_null=True)

    class Meta:
        model = Task
        fields = "__all__"

    def get_flow_task(self, task):
        return get_task_ref(task.flow_task)

    def get_url(self, task):
        return task.flow_task.reverse("index", args=[task.process_id, task.pk])

    def get_title(self, task):
        return task.flow_task.task_title

    def get_description(self, task):
        return task.flow_task.task_description

    def get_brief(self, task):
        return task.brief()

    def get_process_brief(self, task):
        return task.coerced_process.brief

    def get_actions(self, task):
        user = self.context["request"].user
        activation = task.flow_task.activation_class(task)
        return [
            {
                "label": transition.label,
                "conditions_met": transition.conditions_met(activation),
                "has_permission": transition.has_perm(activation, user),
                # 'url': reverse_url(transition.slug)
            }
            for transition in activation.get_outgoing_transitions()
        ]


class LinkedTaskSerializer(serializers.ModelSerializer):
    flow_task = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    owner = UserSerializer(allow_null=True)

    class Meta:
        model = Task
        fields = ["id", "flow_task", "url", "title", "description", "owner", "status"]

    def get_flow_task(self, task):
        return get_task_ref(task.flow_task)

    def get_url(self, task):
        return task.flow_task.reverse("index", args=[task.process_id, task.pk])

    def get_title(self, task):
        return task.flow_task.task_title

    def get_description(self, task):
        return task.flow_task.task_description


class ProcessDetailSerializer(ProcessSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tasks"] = LinkedTaskSerializer(
            source="task_set", many=True, context=self.context
        )


class TaskListSerializer(TaskSerializer):
    def __init__(self, *args, **kwargs):
        super(TaskListSerializer, self).__init__(*args, **kwargs)
        self.fields["process"] = create_serializer(
            self.context["view"].flow_class.process_class, BaseProcessSerializer
        )(context=self.context)
        self.fields["previous"] = LinkedTaskSerializer(many=True, context=self.context)
        self.fields["leading"] = LinkedTaskSerializer(many=True, context=self.context)


def create_serializer(model_class, base_serializer_class, suffix=""):
    class Meta(base_serializer_class.Meta):
        model = model_class

    return type(
        f"{model_class.__name__}{suffix}Serializer",
        (base_serializer_class,),
        {"Meta": Meta},
    )
