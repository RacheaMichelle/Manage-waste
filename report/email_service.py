import threading
import time
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def send_dumping_report(self, report):
        """Send dumping report email with robust error handling"""
        def send_with_retry():
            for attempt in range(self.max_retries):
                try:
                    self._send_report_email(report)
                    logger.info(f"✅ Email sent successfully for report #{report.id}")
                    return True
                    
                except Exception as e:
                    logger.error(f"❌ Email attempt {attempt + 1} failed: {e}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                    else:
                        # Final attempt failed, log and continue
                        logger.error(f"❌ All email attempts failed for report #{report.id}")
                        self._send_fallback_notification(report, str(e))
                        return False
            return False
        
        # Run in background thread
        thread = threading.Thread(target=send_with_retry)
        thread.daemon = True
        thread.start()
    
    def _send_report_email(self, report):
        """Main email sending logic"""
        from .district_contacts import get_district_emails, get_primary_district_contact
        
        subject = f"🚨 Illegal Dumping Report - {report.get_district_display()} District"
        
        # Build reporter information
        reporter_info = self._get_reporter_info(report)
        formatted_date = report.created_at.strftime('%Y-%m-%d at %H:%M:%S')
        
        # Get district email addresses
        district_emails = get_district_emails(report.district)
        
        # Create context for HTML email
        context = {
            'report': report,
            'reporter_info': reporter_info,
            'district_contact': get_primary_district_contact(report.district),
            'formatted_date': formatted_date,
        }
        
        # Render both plain text and HTML versions
        plain_message = self._create_plain_message(report, reporter_info, formatted_date)
        html_message = render_to_string('report/email_report.html', context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=district_emails,
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        
        # Attach HTML version
        email.attach_alternative(html_message, "text/html")
        
        # Try to attach photo (but don't fail if it doesn't work)
        try:
            if report.photo and hasattr(report.photo, 'path'):
                email.attach_file(report.photo.path)
                logger.info("📎 Photo attached to email")
        except Exception as e:
            logger.warning(f"⚠️ Could not attach photo: {e}")
        
        # Send email
        email.send(fail_silently=False)
    
    def _get_reporter_info(self, report):
        """Build reporter information string"""
        if report.reporter_name:
            info = f"Reported by: {report.reporter_name}"
            if report.reporter_email:
                info += f" ({report.reporter_email})"
            if report.reporter_phone:
                info += f" - Phone: {report.reporter_phone}"
            return info
        elif report.user:
            return f"Reported by registered user: {report.user.get_full_name() or report.user.username} ({report.user.email})"
        else:
            return "Reported anonymously"
    
    def _create_plain_message(self, report, reporter_info, formatted_date):
        """Create plain text email content"""
        from .district_contacts import get_primary_district_contact
        
        return f"""
URGENT: Illegal Dumping Report

{reporter_info}

LOCATION DETAILS:
• District: {report.get_district_display()}
• Waste Type: {report.get_waste_type_display()}
• Coordinates: {report.latitude}, {report.longitude}
• Description: {report.description or 'No additional description provided'}

TIMESTAMP: {formatted_date}

DISTRICT CONTACT: {get_primary_district_contact(report.district)}

This report was submitted through the Clean Uganda Platform.
Please take immediate appropriate action.

--
Clean Uganda Environmental Platform
Making Uganda Cleaner, Together
"""
    
    def _send_fallback_notification(self, report, error_message):
        """Send a simple fallback notification when email fails"""
        try:
            # Log the error for admin review
            logger.error(f"""
            📧 EMAIL DELIVERY FAILED
            Report ID: {report.id}
            District: {report.district}
            Error: {error_message}
            Reporter: {report.reporter_name or 'Anonymous'}
            Coordinates: {report.latitude}, {report.longitude}
            """)
            
            # You could also send a notification to admin email here
            # send_mail(
            #     'Email Delivery Failed - Clean Uganda',
            #     f'Failed to send report #{report.id} for {report.district}. Error: {error_message}',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [settings.ADMIN_EMAIL],  # Add this to settings
            #     fail_silently=True,
            # )
            
        except Exception as e:
            logger.error(f"❌ Even fallback notification failed: {e}")

# Global email service instance
email_service = EmailService()
