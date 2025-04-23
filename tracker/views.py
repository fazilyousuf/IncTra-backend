from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Account, Category, Transaction
from .serializers import AccountSerializer, CategorySerializer, TransactionSerializer
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Q


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Show only the current user's accounts
        return Account.objects.filter(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # Optional: Add permissions if categories are user-specific


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MonthlyTotalsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        transactions = Transaction.objects.filter(
            user=request.user,
            date__month=now.month,
            date__year=now.year
        )

        income = transactions.filter(transaction_type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = transactions.filter(transaction_type='EX').aggregate(Sum('amount'))['amount__sum'] or 0

        return Response({
            'income': float(income),
            'expense': float(expense)
        })

class DailyTotalsView(APIView):
    def get(self, request):
        try:
            user = request.user
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=4)  
        
            dates = [start_date + timedelta(days=i) for i in range(5)]
            
            transactions = Transaction.objects.filter(
                user=user,
                date__date__gte=start_date,
                date__date__lte=end_date
            ).values('date__date').annotate(
                income=Sum('amount', filter=Q(transaction_type='IN')),
                expense=Sum('amount', filter=Q(transaction_type='EX'))
            ).order_by('date__date')
            
            # Convert to dictionary for easier processing
            transaction_dict = {t['date__date']: t for t in transactions}
            
            # Fill missing dates with zero values
            daily_totals = []
            for date in dates:
                entry = transaction_dict.get(date, {
                    'date__date': date,
                    'income': 0,
                    'expense': 0
                })
                daily_totals.append({
                    'date': date.strftime('%m-%d'),
                    'income': float(entry['income'] or 0),
                    'expense': float(entry['expense'] or 0)
                })
            
            return Response(daily_totals, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)