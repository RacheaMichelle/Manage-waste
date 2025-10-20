import threading
import time
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.email_timeout = 10  # seconds - matches settings
    
    def send_dumping_report(self, report):
        """Send dumping report email with robust error handling"""
        def send_with_retry():
            for attempt in range(self.max_retries):
                try:
                    success = self._send_report_email(report)
                    if success:
                        logger.info(f"✅ Email sent successfully for report #{report.id}")
                        return True
                    else:
                        logger.warning(f"⚠️ Email sending returned False for report #{report.id}, attempt {attempt + 1}")
                        
                except Exception as e:
                    logger.error(f"❌ Email attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (attempt + 1)
                        logger.info(f"🔄 Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        # Final attempt failed, log and continue
                        logger.error(f"🚨 All email attempts failed for report #{report.id}")
                        self._send_fallback_notification(report, str(e))
                        return False
            return False
        
        # Run in background thread with error handling
        try:
            thread = threading.Thread(target=send_with_retry)
            thread.daemon = True
            thread.start()
            logger.info(f"📧 Email thread started for report #{report.id}")
        except Exception as e:
            logger.error(f"❌ Failed to start email thread: {str(e)}")
            return False
    
    def _send_report_email(self, report):
        """Main email sending logic with timeout handling"""
        try:
            from .district_contacts import get_district_emails, get_primary_district_contact
            
            subject = f"🚨 Illegal Dumping Report - {report.get_district_display()} District"
            
            # Build reporter information
            reporter_info = self._get_reporter_info(report)
            formatted_date = report.created_at.strftime('%Y-%m-%d at %H:%M:%S')
            
            # Get district email addresses
            district_emails = get_district_emails(report.district)
            
            if not district_emails:
                logger.warning(f"⚠️ No email addresses found for district: {report.district}")
                return False
            
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
            
            # Handle photo attachment with timeout protection
            photo_attached = self._attach_photo_safely(email, report)
            if photo_attached:
                logger.info("📎 Photo attached to email")
            
            # Send email with timeout protection
            return self._send_email_safely(email, report.id)
            
        except Exception as e:
            logger.error(f"❌ Error in _send_report_email for report #{report.id}: {str(e)}")
            raise
    
    def _attach_photo_safely(self, email, report):
        """Safely attach photo with error handling"""
        try:
            if report.photo:
                # Check if photo file exists and is accessible
                if hasattr(report.photo, 'path'):
                    # Use Django's storage system for better compatibility
                    if default_storage.exists(report.photo.name):
                        email.attach_file(report.photo.path)
                        return True
                    else:
                        logger.warning(f"⚠️ Photo file not found: {report.photo.name}")
                else:
                    logger.warning("⚠️ Report photo has no path attribute")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Could not attach photo: {str(e)}")
            return False
    
    def _send_email_safely(self, email, report_id):
        """Send email with timeout protection"""
        def send_email_with_timeout():
            try:
                email.send(fail_silently=False)
                return True
            except Exception as e:
                logger.error(f"❌ Email sending failed in thread for report #{report_id}: {str(e)}")
                return False
        
        # Use threading with timeout
        result = [False]  # Use list to store result from thread
        exception = [None]
        
        def target():
            try:
                result[0] = send_email_with_timeout()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.email_timeout)
        
        if thread.is_alive():
            logger.error(f"⏰ Email sending timed out after {self.email_timeout}s for report #{report_id}")
            return False
        
        if exception[0]:
            logger.error(f"❌ Email thread exception for report #{report_id}: {str(exception[0])}")
            return False
        
        return result[0]
    
    def _get_reporter_info(self, report):
        """Build reporter information string"""
        try:
            if report.reporter_name:
                info = f"Reported by: {report.reporter_name}"
                if report.reporter_email:
                    info += f" ({report.reporter_email})"
                if report.reporter_phone:
                    info += f" - Phone: {report.reporter_phone}"
                return info
            elif report.user:
                user = report.user
                name = user.get_full_name() or user.username
                return f"Reported by registered user: {name} ({user.email})"
            else:
                return "Reported anonymously"
        except Exception as e:
            logger.warning(f"⚠️ Error building reporter info: {str(e)}")
            return "Reporter information unavailable"
    
    def _create_plain_message(self, report, reporter_info, formatted_date):
        """Create plain text email content"""
        try:
            from .district_contacts import get_primary_district_contact
            
            district_contact = "Contact information not available"
            try:
                district_contact = get_primary_district_contact(report.district)
            except Exception:
                pass
            
            return f"""
URGENT: Illegal Dumping Report

{reporter_info}

LOCATION DETAILS:
• District: {report.get_district_display()}
• Waste Type: {report.get_waste_type_display()}
• Coordinates: {report.latitude}, {report.longitude}
• Description: {report.description or 'No additional description provided'}

TIMESTAMP: {formatted_date}

DISTRICT CONTACT: {district_contact}

This report was submitted through the Clean Uganda Platform.
Please take immediate appropriate action.

--
Clean Uganda Environmental Platform
Making Uganda Cleaner, Together
"""
        except Exception as e:
            logger.error(f"❌ Error creating plain message: {str(e)}")
            return f"Emergency report - District: {report.district}, Location: {report.latitude}, {report.longitude}"
    
    def _send_fallback_notification(self, report, error_message):
        """Send a simple fallback notification when email fails"""
        try:
            # Log the error for admin review
            logger.error(f"""
📧 EMAIL DELIVERY FAILED
Report ID: {report.id}
District: {report.get_district_display()}
Error: {error_message}
Reporter: {report.reporter_name or 'Anonymous'}
Coordinates: {report.latitude}, {report.longitude}
Time: {report.created_at}
            """)
            
            # Alternative: Send simple email without attachments
            self._send_minimal_email(report, error_message)
            
        except Exception as e:
            logger.error(f"❌ Even fallback notification failed: {str(e)}")
    
    def _send_minimal_email(self, report, error_message):
        """Send minimal email as last resort"""
        try:
            from .district_contacts import get_district_emails
            
            district_emails = get_district_emails(report.district)
            if not district_emails:
                return
            
            subject = f"URGENT: Dumping Report - {report.get_district_display()}"
            message = f"""
Quick Report - Email system had issues

District: {report.get_district_display()}
Waste Type: {report.get_waste_type_display()}
Location: {report.latitude}, {report.longitude}
Reporter: {report.reporter_name or 'Anonymous'}

Original error: {error_message}

Please check the Clean Uganda admin dashboard for full details.
"""
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=district_emails,
                fail_silently=True  # Don't raise exceptions here
            )
            logger.info(f"📨 Minimal email sent for report #{report.id}")
            
        except Exception as e:
            logger.error(f"❌ Minimal email also failed: {str(e)}")

# Global email service instance
email_service = EmailService()
