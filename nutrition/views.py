from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition.models import NutritionPlan
from payments.models import Subscription

from .serializers import NutritionPlanSerializer


class MyNutritionView(APIView):
    def get(self, request):
        subscription = (
            Subscription.objects.filter(user=request.user, status=Subscription.Status.ACTIVE)
            .select_related("program")
            .order_by("-start_date")
            .first()
        )
        if subscription is None:
            return Response({"plan": None})
        try:
            plan = subscription.program.nutrition_plan
        except NutritionPlan.DoesNotExist:
            return Response({"plan": None})
        return Response({"plan": NutritionPlanSerializer(plan).data})
