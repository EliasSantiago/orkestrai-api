"""OAuth token manager for on-premise API authentication."""

import time
import base64
import httpx
from typing import Optional, Dict
from src.config import Config


class OAuthTokenManager:
    """Manages OAuth token generation and caching for on-premise APIs."""
    
    def __init__(self):
        self.token_cache: Optional[Dict[str, any]] = None
        self.token_expires_at: float = 0
        self.token_url = Config.ONPREMISE_TOKEN_URL
        self.consumer_key = Config.ONPREMISE_CONSUMER_KEY
        self.consumer_secret = Config.ONPREMISE_CONSUMER_SECRET
        self.username = Config.ONPREMISE_USERNAME
        self.password = Config.ONPREMISE_PASSWORD
        self.grant_type = Config.ONPREMISE_OAUTH_GRANT_TYPE or "client_credentials"
        
        # Validate required configuration
        if not self.token_url:
            raise ValueError("ONPREMISE_TOKEN_URL not configured")
        if not self.consumer_key or not self.consumer_secret:
            raise ValueError("ONPREMISE_CONSUMER_KEY and ONPREMISE_CONSUMER_SECRET must be configured")
        
        # For password grant, username and password are required
        # For client_credentials grant, they are not needed
        if self.grant_type == "password":
            if not self.username or not self.password:
                raise ValueError(
                    "ONPREMISE_USERNAME and ONPREMISE_PASSWORD are required for OAuth password grant. "
                    "If your API uses client_credentials grant, set ONPREMISE_OAUTH_GRANT_TYPE=client_credentials"
                )
    
    def _generate_basic_auth_header(self) -> str:
        """Generate Basic Auth header from consumer key and secret."""
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    async def get_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid OAuth token, using cache if available.
        
        Args:
            force_refresh: Force token refresh even if cached token is still valid
            
        Returns:
            OAuth access token string
        """
        # Check if we have a valid cached token
        current_time = time.time()
        if not force_refresh and self.token_cache and current_time < self.token_expires_at:
            return self.token_cache.get("access_token", "")
        
        # Generate new token
        try:
            # Prepare Basic Auth header
            auth_header = self._generate_basic_auth_header()
            
            # Prepare request data based on grant type
            data = {
                "grant_type": self.grant_type
            }
            
            # Add username/password only for password grant
            if self.grant_type == "password":
                data["username"] = self.username
                data["password"] = self.password
            # For client_credentials, only consumer key/secret in Basic Auth header is needed
            
            # Configure SSL verification
            verify_ssl = Config.VERIFY_SSL
            
            print(f"🔐 Gerando token OAuth: {self.token_url} (grant_type={self.grant_type})")
            
            # Make token request
            async with httpx.AsyncClient(timeout=30.0, verify=verify_ssl) as client:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={
                        "Authorization": auth_header,
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
                
                print(f"📡 Resposta do token: HTTP {response.status_code}")
                
                if response.status_code != 200:
                    error_text = response.text
                    print(f"✗ Erro ao gerar token: {response.status_code} - {error_text}")
                    raise Exception(
                        f"Failed to generate OAuth token: HTTP {response.status_code} - {error_text}"
                    )
                
                token_data = response.json()
                
                # Cache token
                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
                
                if not access_token:
                    raise Exception("Token response does not contain access_token")
                
                # Cache token with expiration (subtract 60 seconds for safety margin)
                self.token_cache = token_data
                self.token_expires_at = current_time + expires_in - 60
                
                print(f"✓ Token OAuth gerado com sucesso (expira em {expires_in}s)")
                return access_token
                
        except httpx.TimeoutException:
            raise Exception("Timeout ao gerar token OAuth. Verifique a conectividade com o servidor.")
        except httpx.ConnectError as e:
            error_msg = str(e)
            if "CERTIFICATE_VERIFY_FAILED" in error_msg or "certificate verify failed" in error_msg.lower():
                raise Exception(
                    "Erro de certificado SSL ao gerar token OAuth. "
                    "Adicione no .env: VERIFY_SSL=false (⚠️ ATENÇÃO: Inseguro, use apenas em desenvolvimento)"
                )
            else:
                raise Exception(
                    f"Erro de conexão ao gerar token OAuth: {error_msg}. "
                    f"Verifique se o servidor está acessível em: {self.token_url}"
                )
        except Exception as e:
            raise Exception(f"Erro ao gerar token OAuth: {str(e)}")
    
    def clear_cache(self):
        """Clear cached token (force refresh on next request)."""
        self.token_cache = None
        self.token_expires_at = 0

