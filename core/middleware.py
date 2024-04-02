from django.contrib.sessions.models import Session
from .models import UserSession
from datetime import timezone,datetime,timedelta
from django.contrib.auth import logout


class UserSessionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            session_key = request.session.session_key
            ip_address = request.META.get('REMOTE_ADDR')

            try:

                session = Session.objects.get(session_key=session_key)
                user_session = UserSession.objects.get(session=session)
                # Check if the session has expired
                if session.expire_date < datetime.now(timezone.utc):
                    logout(request)  # Log out the user if the session has expired
                else:
                    # Update end_datetime to 2 hours from now
                    user_session.end_datetime = datetime.now(timezone.utc) + timedelta(hours=2)
                    user_session.save()
                    
            except UserSession.DoesNotExist:
                user = request.user
                session = Session.objects.get(session_key=session_key)
                user_session = UserSession.objects.create(session=session,user=user, ip_address=ip_address)

        response = self.get_response(request)

        return response
