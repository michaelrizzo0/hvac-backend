# api/mixins.py

from .models import AuditLog, Client

class AuditLoggingMixin:
    """
    A mixin that automatically logs create, update, and delete actions.
    """
    def get_client_from_instance(self, instance):
        """
        Helper method to find the client associated with any given model instance.
        This is necessary because the AuditLog is always tied to a Client.
        """
        if isinstance(instance, Client):
            return instance
        if hasattr(instance, 'client') and instance.client:
            return instance.client
        if hasattr(instance, 'equipment') and instance.equipment:
            return instance.equipment.client
        # Handle attachments by checking their parent object
        if hasattr(instance, 'service_history') and instance.service_history:
            return instance.service_history.equipment.client
        if hasattr(instance, 'invoice') and instance.invoice:
            return instance.invoice.client
        return None

    def perform_create(self, serializer):
        instance = serializer.save()
        client = self.get_client_from_instance(instance)
        if client and self.request.user.is_authenticated:
            AuditLog.objects.create(
                user=self.request.user,
                client=client,
                action=f"CREATED {instance.__class__.__name__}",
                metadata={'details': str(instance)}
            )

    def perform_update(self, serializer):
        instance = serializer.save()
        client = self.get_client_from_instance(instance)
        if client and self.request.user.is_authenticated:
            AuditLog.objects.create(
                user=self.request.user,
                client=client,
                action=f"UPDATED {instance.__class__.__name__}",
                metadata={'details': str(instance)}
            )

    def perform_destroy(self, instance):
        client = self.get_client_from_instance(instance)
        details = str(instance)
        model_name = instance.__class__.__name__

        # We must log before deleting to preserve the client relationship
        if client and self.request.user.is_authenticated:
            AuditLog.objects.create(
                user=self.request.user,
                client=client,
                action=f"DELETED {model_name}",
                metadata={'details': str(instance)}
            )

        instance.delete()