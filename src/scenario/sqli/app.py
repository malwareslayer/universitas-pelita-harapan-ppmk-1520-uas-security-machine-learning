from parser import GenerateVulnSQLInjectionEndpoint

from .schema import Base

app = GenerateVulnSQLInjectionEndpoint(__name__, 'sqlite:///db/main.db', Base, 'sqlite')


__all__ = ['app']
