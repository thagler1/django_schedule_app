
@shared_task
def add(x, y):
    from .models import UserProfile
    return x + y

