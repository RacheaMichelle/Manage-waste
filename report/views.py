from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail
from .forms import DumpingReportForm
from .models import DumpingReport
from .district_contacts import get_primary_district_contact
from .email_service import email_service  # Import the new simple email service

def report_dumping(request):
    if request.method == 'POST':
        form = DumpingReportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                report = form.save(commit=False)
                
                # If user is logged in, associate with their account
                if request.user.is_authenticated:
                    report.user = request.user
                
                report.save()
                
                # Send SMS notification (console log for now)
                district_number = get_primary_district_contact(report.district)
                sms_content = (
                    f"New dumping report in {report.district}\n"
                    f"Type: {report.get_waste_type_display()}\n"
                    f"Location: {report.latitude}, {report.longitude}"
                )
                print(f"\nSMS would be sent to {district_number}:\n{sms_content}\n")
                
                # Send email using the SIMPLE service (no attachments, no threading)
                email_sent = email_service.send_dumping_report(report)
                
                if email_sent:
                    messages.success(request, 
                        "Thank you! Your report has been submitted successfully. "
                        "Authorities have been notified through our system."
                    )
                else:
                    messages.warning(request, 
                        "Thank you! Your report has been submitted successfully. "
                        "There was a temporary issue with email notifications, but your report has been logged."
                    )
                
                return redirect('report_success', report_id=report.id)
                
            except Exception as e:
                messages.error(request, 
                    "Your report was saved, but there was an issue with notifications. "
                    "The authorities will still receive your report through our system."
                )
                # Log the error but don't crash the user experience
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Report submission error: {e}")
                return redirect('report_success', report_id=report.id)
    else:
        # Pre-fill location if available from logged-in user
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['reporter_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
            initial_data['reporter_email'] = request.user.email
        
        form = DumpingReportForm(initial=initial_data)
    
    return render(request, 'report/report_form.html', {'form': form})

def report_success(request, report_id):
    try:
        report = DumpingReport.objects.get(id=report_id)
        return render(request, 'report/report_success.html', {'report': report})
    except DumpingReport.DoesNotExist:
        messages.error(request, "Report not found.")
        return redirect('report_dumping')

# Test email view (remove in production)
def test_email(request):
    """Test email configuration"""
    if not settings.DEBUG:
        return HttpResponse("Test email only available in debug mode.", status=403)
    
    try:
        # Test simple email
        send_mail(
            '✅ Test Email from Clean Uganda',
            'Congratulations! Your email configuration is working correctly.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # Send to yourself for testing
            fail_silently=False,
        )
        
        return HttpResponse("""
            <div style="text-align: center; padding: 50px; background: #f0f9ff;">
                <h1 style="color: #059669;">✅ Email Test Successful!</h1>
                <p style="font-size: 18px;">Test email sent successfully.</p>
                <p>Check your email inbox for the test message.</p>
                <a href="/report/report/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px;">
                    Back to Reporting
                </a>
            </div>
        """)
    except Exception as e:
        return HttpResponse(f"""
            <div style="text-align: center; padding: 50px; background: #fef2f2;">
                <h1 style="color: #dc2626;">❌ Email Test Failed</h1>
                <p style="font-size: 18px;">Error: {e}</p>
                <p>Check your email settings in settings.py</p>
                <p><strong>Note:</strong> On Render free tier, outbound SMTP may be blocked.</p>
                <a href="/report/report/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px;">
                    Back to Reporting
                </a>
            </div>
        """)
