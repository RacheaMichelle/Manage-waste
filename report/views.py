# report/email_service.py
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

class SimpleEmailService:
    def send_dumping_report(self, report):
        """Send simplified dumping report email without attachments"""
        try:
            subject = f"🚨 Illegal Dumping Report - {report.get_district_display()}"
            
            message = f"""
URGENT: Illegal Dumping Report

Location Details:
• District: {report.get_district_display()}
• Waste Type: {report.get_waste_type_display()} 
• Coordinates: {report.latitude}, {report.longitude}
• Description: {report.description or 'No additional description provided'}

Reporter: {report.reporter_name or 'Anonymous'}
Timestamp: {report.created_at.strftime('%Y-%m-%d at %H:%M:%S')}

Please check the Clean Uganda dashboard for photos and detailed information.

--
Clean Uganda Environmental Platform
Making Uganda Cleaner, Together
"""
            # Use a simple recipient for testing
            recipient_list = ['admin@cleanuganda.com']  # Replace with actual district emails
            
            # Send simple email without attachments
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False
            )
            
            logger.info(f"✅ Email sent successfully for report #{report.id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Email failed for report #{report.id}: {str(e)}")
            # Log the report details for manual follow-up
            self._log_report_for_manual_followup(report, str(e))
            return False
    
    def _log_report_for_manual_followup(self, report, error):
        """Log report details for manual follow-up when email fails"""
        logger.error(f"""
📧 EMAIL FAILED - MANUAL FOLLOWUP REQUIRED
Report ID: {report.id}
District: {report.get_district_display()}
Waste Type: {report.get_waste_type_display()}
Location: {report.latitude}, {report.longitude}
Reporter: {report.reporter_name or 'Anonymous'}
Error: {error}
Time: {report.created_at}
        """)

# Global email service instance
email_service = SimpleEmailService()
