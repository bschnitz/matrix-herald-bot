from nio import ErrorResponse

class NioErrorResponseException(Exception):
    """Exception wrapper für nio ErrorResponse-Objekte.  
      
    Attributes:  
        error (ErrorResponse): Das ursprüngliche ErrorResponse-Objekt  
        message (str): Die Fehlermeldung  
        status_code (str, optional): Der Matrix-Fehlercode  
        retry_after_ms (int, optional): Retry-Verzögerung bei Rate-Limiting  
    """

    def __init__(self, error: ErrorResponse):
        self.error = error
        self.message = error.message
        self.status_code = error.status_code
        self.retry_after_ms = error.retry_after_ms
        self.soft_logout = error.soft_logout

        # Exception-Message basierend auf ErrorResponse.__str__()
        super().__init__(str(error))

    def __repr__(self):
        return f"NioErrorResponseException({self.error!r})"
