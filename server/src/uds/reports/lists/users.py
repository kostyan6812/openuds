# -*- coding: utf-8 -*-

#
# Copyright (c) 2015 Virtual Cable S.L.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#    * Neither the name of Virtual Cable S.L. nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
.. moduleauthor:: Adolfo Gómez, dkmaster at dkmon dot com
'''
from __future__ import unicode_literals

from django.utils.translation import ugettext, ugettext_noop as _
from uds.core.ui.UserInterface import gui
from uds.core.reports import stock
from uds.models import Authenticator
import StringIO

from .base import ListReport

from uds.core.util import tools
from geraldo.generators.pdf import PDFGenerator
from geraldo import Report, landscape, ReportBand, ObjectValue, SystemField, BAND_WIDTH, Label, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

import logging

logger = logging.getLogger(__name__)

__updated__ = '2015-04-29'


class UsersReport(Report):
    title = 'Test report'
    author = 'UDS Enterprise'

    print_if_empty = True
    page_size = A4
    margin_left = 2 * cm
    margin_top = 0.5 * cm
    margin_right = 0.5 * cm
    margin_bottom = 0.5 * cm

    class band_detail(ReportBand):
        height = 0.5 * cm
        elements = (
            ObjectValue(attribute_name='name', left=0.5 * cm),
            ObjectValue(attribute_name='real_name', left=3 * cm),
            ObjectValue(attribute_name='last_access', left=7 * cm),
        )

    class band_page_header(ReportBand):
        height = 2.0 * cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.5 * cm, left=0, width=BAND_WIDTH,
                        style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),

            Label(text="User ID", top=1.5 * cm, left=0.5 * cm),
            Label(text="Real Name", top=1.5 * cm, left=3 * cm),
            Label(text="Last access", top=1.5 * cm, left=7 * cm),
            SystemField(expression=_('Page %(page_number)d of %(page_count)d'), top=0.1 * cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            Image(filename=stock.getStockImagePath(stock.LOGO), left=0.1 * cm, top=0.0 * cm, width=2 * cm, height=2 * cm),
        ]
        borders = {'bottom': True}

    class band_page_footer(ReportBand):
        height = 0.5 * cm
        elements = [
            Label(text='Generated by UDS', top=0.1 * cm),
            SystemField(expression=_('Printed in %(now:%Y, %b %d)s at %(now:%H:%M)s'), top=0.1 * cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
        ]
        borders = {'top': True}


class ListReportUsers(ListReport):
    filename = 'users.pdf'

    def initialize(self, values):
        if values:
            auth = Authenticator.objects.get(uuid=self.authenticator.value)
            self.filename = auth.name + '.pdf'

    authenticator = gui.ChoiceField(
        label=_("Authenticator"),
        order=1,
        tooltip=_('Authenticator from where to list users'),
        required=True
    )

    name = _('Users list')  # Report name
    description = _('List users of platform')  # Report description
    uuid = '8cd1cfa6-ed48-11e4-83e5-10feed05884b'

    def initGui(self):
        logger.debug('Initializing gui')
        vals = [
            gui.choiceItem(v.uuid, v.name) for v in Authenticator.objects.all()
        ]

        self.authenticator.setValues(vals)

    def generate(self):
        auth = Authenticator.objects.get(uuid=self.authenticator.value)
        users = auth.users.order_by('name')

        output = StringIO.StringIO()

        report = UsersReport(queryset=users)
        report.title = _('Users List for {}').format(auth.name)
        report.generate_by(PDFGenerator, filename=output)
        return output.getvalue()
