from rest_framework.throttling import AnonRateThrottle


class ContactThrottle(AnonRateThrottle):
    scope = "contact"


class AuthThrottle(AnonRateThrottle):
    scope = "auth"
