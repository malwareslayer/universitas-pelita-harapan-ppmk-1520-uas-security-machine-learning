from parser.generator import GenerateVulnSQLInjectionEndpoint

from .schema import Base

app = GenerateVulnSQLInjectionEndpoint(__name__, Base, 'sqlite')


__all__ = ['app']
