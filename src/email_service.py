"""Email service for sending password reset emails."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from src.config import Config


def send_password_reset_email(email: str, reset_token: str, reset_url: str) -> bool:
    """
    Send password reset email to user.
    
    Args:
        email: User's email address
        reset_token: Password reset token
        reset_url: Full URL for password reset (includes token)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    # Check if email is configured
    if not Config.SMTP_USER or not Config.SMTP_PASSWORD:
        print(f"⚠ Email not configured. Would send reset link to {email}: {reset_url}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Recuperação de Senha - Agents ADK API"
        msg['From'] = f"{Config.SMTP_FROM_NAME} <{Config.SMTP_FROM_EMAIL}>"
        msg['To'] = email
        
        # Create HTML email body
        html_body = f"""
        <html>
          <body>
            <h2>Recuperação de Senha</h2>
            <p>Olá,</p>
            <p>Você solicitou a recuperação de senha para sua conta na Agents ADK API.</p>
            <p>Clique no link abaixo para redefinir sua senha:</p>
            <p><a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Redefinir Senha</a></p>
            <p>Ou copie e cole este link no seu navegador:</p>
            <p style="word-break: break-all; color: #666;">{reset_url}</p>
            <p><strong>Este link expira em {Config.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} horas.</strong></p>
            <p>Se você não solicitou esta recuperação de senha, ignore este email.</p>
            <hr>
            <p style="color: #999; font-size: 12px;">Este é um email automático, por favor não responda.</p>
          </body>
        </html>
        """
        
        # Create plain text email body
        text_body = f"""
        Recuperação de Senha
        
        Olá,
        
        Você solicitou a recuperação de senha para sua conta na Agents ADK API.
        
        Clique no link abaixo para redefinir sua senha:
        {reset_url}
        
        Este link expira em {Config.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} horas.
        
        Se você não solicitou esta recuperação de senha, ignore este email.
        
        ---
        Este é um email automático, por favor não responda.
        """
        
        # Attach both parts
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_USE_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"✗ Error sending email to {email}: {str(e)}")
        return False

