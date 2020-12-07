# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from optparse import make_option

import ldap
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "[NOT FINISHED] Fetch list of lecturers, add them to a blacklist."
    option_list = BaseCommand.option_list + (
        make_option("--user", dest="username", help="HSR username"),
        make_option("--pass", dest="password", help="HSR password"),
    )

    def printO(self, msg, newline=True):
        """Print to stdout. This expects unicode strings!"""
        encoding = self.stdout.encoding or sys.getdefaultencoding()
        self.stdout.write(msg.encode(encoding, "replace"))
        if newline:
            self.stdout.write("\n")

    def printE(self, msg, newline=True):
        """Print to stderr. This expects unicode strings!"""
        encoding = self.stderr.encoding or sys.getdefaultencoding()
        self.stderr.write(msg.encode(encoding, "replace"))
        if newline:
            self.stdout.write("\n")

    def handle(self, **options):
        assert "username" in options, "--user argument required"
        assert options["username"], "--user argument required"
        assert "password" in options, "--pass argument required"
        assert options["password"], "--pass argument required"
        # pw = getpass.getpass()  # TODO
        pw = options["password"]

        dn = "CN=%s,OU=Stud,OU=HSR,OU=FH_Users,DC=hsr,DC=ch" % options["username"]
        con = ldap.initialize("ldap://hsr.ch:389")
        # con.protocol_version = ldap.VERSION3
        con.simple_bind_s(dn, pw)

        print("bound")

        # basedn_stud = 'OU=Stud,OU=HSR,OU=FH_Users,DC=hsr,DC=ch'
        basedn_pers = "OU=Pers,OU=HSR,OU=FH_Users,DC=hsr,DC=ch"

        # fltr = ''
        # attrs = ['cn']

        result = con.search_s(
            basedn_pers, ldap.SCOPE_SUBTREE, "(objectClass=*)", ["cn", "mail"]
        )

        print("gotten result")

        from pprint import pprint

        pprint(result)
        # result_data = con.result(result_id, 0)
        # print result_data
