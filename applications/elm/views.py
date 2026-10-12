from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import LeaveApplication, LeaveBalance
from django.db import transaction
from datetime import datetime

class ReviewLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        decision = request.data.get('decision')  # 'approve', 'reject', 'recommend'
        try:
            with transaction.atomic():
                leave = LeaveApplication.objects.select_for_update().get(pk=pk, status='AWAITING_UNIT_HEAD')

                if leave.category in ['CL', 'RH', 'SCL', 'EL', 'COL', 'VL']:
                    duration = (leave.end_date - leave.start_date).days + 1

                    if decision == 'approve':
                        leave.status = 'APPROVED'
                        # Deduct leave balance
                        balance = LeaveBalance.objects.get(user=leave.applicant, year=datetime.now().year)
                        if decision == 'approve':
                            if leave.category == 'CL':
                                if balance.casual_leave < duration:
                                    raise ValueError("Insufficient leave balance for approval")
                                balance.casual_leave -= duration
                            elif leave.category == 'RH':
                                if balance.restricted_holiday < duration:
                                    raise ValueError("Insufficient leave balance for approval")
                                balance.restricted_holiday -= duration
                            elif leave.category == 'SCL':
                                if balance.special_casual_leave < duration:
                                    raise ValueError("Insufficient leave balance for approval")
                                balance.special_casual_leave -= duration
                            elif leave.category == 'EL':
                                if balance.earned_leave < duration:
                                    raise ValueError("Insufficient leave balance for approval")
                                balance.earned_leave -= duration
                            elif leave.category == 'COL':
                                if balance.commuted_leave < duration:
                                    raise ValueError("Insufficient leave balance for approval")
                                balance.commuted_leave -= duration
                            elif leave.category == 'VL':
                                if balance.vacation_leave < duration:
                                    raise ValueError("Insufficient leave balance for approval")
                                balance.vacation_leave -= duration
                        balance.save()
                    elif decision == 'reject':
                        leave.status = 'REJECTED'
                    elif decision == 'recommend':
                        leave.status = 'AWAITING_FINAL'

                leave.save()
                return Response({"message": f"Leave review updated to {leave.status}"})
        except LeaveApplication.DoesNotExist:
            return Response({"error": "Leave application not found"}, status=status.HTTP_404_NOT_FOUND)
        except LeaveBalance.DoesNotExist:
            return Response({"error": "Leave balance record not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
