from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from config.throttles import ContactThrottle

from .serializers import ContactInquirySerializer


class ContactCreateView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ContactThrottle]

    def post(self, request):
        serializer = ContactInquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Inquiry received."}, status=status.HTTP_201_CREATED)
