from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import LeaveApplication, LeaveBalance

class RespondSubstituteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        action = request.data.get('action') # 'accept' or 'decline'
        try:
            leave = LeaveApplication.objects.get(pk=pk, substitute=request.user, status='AWAITING_SUBSTITUTE')
            if action == 'accept':
                leave.status = 'AWAITING_UNIT_HEAD' # BR-EL-015: Release consent gate
                leave.save()
                return Response({"message": "Substitute responsibility accepted"})
            elif action == 'decline':
                leave.status = 'APPLICANT_ACTION_REQUIRED' # BR-EL-015: Set action required
                leave.save()
                return Response({"message": "Substitute responsibility declined"})
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        except LeaveApplication.DoesNotExist:
            return Response({"error": "Pending substitute request not found"}, status=status.HTTP_404_NOT_FOUND)

class ReviewLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        decision = request.data.get('decision') # 'approve', 'reject', 'recommend'
        try:
            leave = LeaveApplication.objects.get(pk=pk, status='AWAITING_UNIT_HEAD')
            
            # BR-EL-016: CL and RH final sanction at Unit Head
            if leave.category in ['CL', 'RH']:
                if decision == 'approve':
                    leave.status = 'APPROVED'
                else:
                    leave.status = 'REJECTED'
            # BR-EL-017: SCL, EL, COL, VL require higher sanction routing
            else:
                leave.status = 'AWAITING_FINAL' if decision in ['recommend', 'approve'] else 'REJECTED'
                
            leave.save()
            return Response({"message": f"Leave review updated to {leave.status}"})
        except LeaveApplication.DoesNotExist:
            return Response({"error": "Leave application not found"}, status=status.HTTP_404_NOT_FOUND)