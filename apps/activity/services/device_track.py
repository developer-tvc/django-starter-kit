from apps.activity.models import UserDevice

def track_device(request, user):
    device_id = getattr(request, "device_id", None)

    if not device_id:
        return

    device, created = UserDevice.objects.get_or_create(
        user=user,
        device_id=device_id,
        defaults={
            "user_agent": request.user_agent,
            "ip_address": request.ip_address,
        }
    )

    if not created:
        device.ip_address = request.ip_address
        device.user_agent = request.user_agent
        device.is_active = True
        device.save()