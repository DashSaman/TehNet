class RubikaDisabled(RuntimeError):pass

class RubikaBackend:
    """No accounts, tokens, uploads or public/private redirect support is implemented."""
    def __init__(self,*args,**kwargs):raise RubikaDisabled('Rubika remains unapproved and disabled')
