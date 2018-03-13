from itertools import groupby
from datetime import datetime, timedelta
from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo import api, fields, models, _
import datetime
# from odoo.osv import expression.
import odoo.addons.decimal_precision as dp
import os.path
import tempfile
import base64
import StringIO
import io
import urllib2
from datetime import date
import pandas as pd
from xlwt import *
from openerp.exceptions import AccessError, _logger
from pandas import DataFrame
try:
    import xlwt
except:
    raise exceptions.ValidationError('Warning ! python-xlwt module missing. Please install it.')


class CMSReport(models.TransientModel):
    _name ='cms.report.data'
    _description = 'CMS Report'
    _rec_name = 'file_name'

    season = fields.Char('Season')
    ryot_number_id = fields.Many2many('ryot.bill',string='Ryot Number')
    company_id = fields.Many2one('res.company',string='Company Name', default=lambda self: self.env['res.company']._company_default_get('cms.report.data'))
    from_date = fields.Date('From Date')
    to_date = fields.Date('Till Date')
    file_output = fields.Binary(string="File Output", readonly=True, help='Output file in xlsx format')
    file_name = fields.Char(string='File Name', invisible=True)

    def reset_cms_report(self):
        self.write({
            'season':None,
            'ryot_number_id': None,
            'from_date': None,
            'to_date': None,
            'file_output': None,
            'file_name': None,
        })

    def generate_ryot_final_report(self):
        report_season = self.season
        row = 1
        row1 = 1
        row2 = 1
        writer = pd.ExcelWriter('/tmp/Ryot_bill.xls', engine='xlsxwriter')
        for rec in self.ryot_number_id:
            ryot_number = rec.ryot_number
            start = self.from_date
            end = self.to_date
            if start and end:
                self.env.cr.execute("""select rb.processid,to_char(rb.from_date, 'DD-MM-YYYY') as from_date,to_char(rb.to_date, 'DD-MM-YYYY') as to_date,rb.net_weight,
                                                                            rb.cane_price,rb.gross_amount,rb.tnwf,rb.harvest_amount,rb.advance,rb.material,rb.seed,rb.service,rb.bad_cane, (rb.tnwf+rb.harvest_amount+rb.advance) as total,rb.net_pay,rb.payment_type,rb.bank,
                                                                            rb.branch,rb.account_no
                                                                            from ryot_bill as rb
                                                                            where rb.season =%(season)s
                                                                            and rb.ryot_number =%(ryot_number)s
                                                                            and rb.from_date >= %(from_date)s
                                                                            and rb.to_date <= %(to_date)s
                                                                            order by id""",
                                    {'season': report_season, 'ryot_number': ryot_number, 'from_date': start,
                                     'to_date': end})
            else:
                self.env.cr.execute("""select rb.processid,to_char(rb.from_date, 'DD-MM-YYYY') as from_date,to_char(rb.to_date, 'DD-MM-YYYY') as to_date,rb.net_weight,
                                                                                        rb.cane_price,rb.gross_amount,rb.tnwf,rb.harvest_amount,rb.advance,rb.material,rb.seed,rb.service,rb.bad_cane, (rb.tnwf+rb.harvest_amount+rb.advance) as total,rb.net_pay,rb.payment_type,rb.bank,
                                                                                        rb.branch,rb.account_no
                                                                                        from ryot_bill as rb
                                                                                        where rb.season =%(season)s
                                                                                        and rb.ryot_number =%(ryot_number)s
                                                                                        order by id""",
                                        {'season': report_season, 'ryot_number': ryot_number})
                print report_season, ryot_number, "SSSSSSSSSSS"

            df = DataFrame(self.env.cr.dictfetchall(),
                           columns=['processid', 'from_date', 'to_date', 'net_weight', 'cane_price', 'gross_amount',
                                    'tnwf', 'harvest_amount', 'advance', 'material', 'seed', 'service', 'bad_cane',
                                    'total', 'net_pay', 'payment_type', 'bank', 'branch', 'account_no'])


            if start and end:
                self.env.cr.execute("""select to_char(cw.weighment_date, 'DD-MM-YYYY') as weighment_date,cw.weighment_no,cw.plot_number,
                                                                                    cw.gross_weight,
                                                                                    cw.tare_weight,cw.bind_qty,cw.net_weight,
                                                                                    cw.gl_name,cw.labour_rate,
                                                                                    cw.transporter_name,cw.vehicle_no,cw.transportor_charge,cw.diesel_qty
                                                                                    from cane_weighment as cw
                                                                                    where cw.season =%(season)s
                                                                                    and cw.ryot_number =%(ryot_number)s
                                                                                    and cw.weighment_date >= %(from_date)s
                                                                                    and cw.weighment_date <= %(to_date)s
                                                                                    order by cw.weighment_date asc""",
                                    {'season': report_season, 'ryot_number': ryot_number, 'from_date': start,
                                     'to_date': end})
            else:
                self.env.cr.execute("""select to_char(cw.weighment_date, 'DD-MM-YYYY') as weighment_date,cw.weighment_no,cw.plot_number,
                                                                                                cw.gross_weight,
                                                                                                cw.tare_weight,cw.bind_qty,cw.net_weight,
                                                                                                cw.gl_name,cw.labour_rate,
                                                                                                cw.transporter_name,cw.vehicle_no,cw.transportor_charge,cw.diesel_qty
                                                                                                from cane_weighment as cw
                                                                                                where cw.season =%(season)s
                                                                                                and cw.ryot_number =%(ryot_number)s
                                                                                                order by cw.weighment_date asc""",
                                    {'season': report_season, 'ryot_number': ryot_number})

            df1 = DataFrame(self.env.cr.dictfetchall(),
                            columns=['weighment_date', 'weighment_no', 'plot_number', 'gross_weight', 'tare_weight',
                                     'bind_qty', 'net_weight', 'gl_name', 'labour_rate', 'transporter_name',
                                     'vehicle_no', 'transportor_charge', 'diesel_qty'])

            print 'sss'

            count_row = len(df['processid'])
            df1_count = len(df1['weighment_date'])
            tonnes = df['net_weight'].sum()
            gross_amount = df['gross_amount'].sum()
            tnwf = df['tnwf'].sum()
            harvest_amount = df['harvest_amount'].sum()
            gross_weight = df1['gross_weight'].sum()
            tare_weight = df1['tare_weight'].sum()
            net_weight = df1['net_weight'].sum()
            bind_qty = df1['bind_qty'].sum()

            print row,'row0'
            ros = (row2-row)
            print ros,'ros'
            row = row + 5 +ros
            print row,'row'
            row_count = row + 4
            print row_count,'row_count'
            print count_row,'df_count'
            row1 = row_count + count_row + 4
            print row1,'row1'
            row2 = row1+df1_count+1
            print row2,'row2'

            df.to_excel(writer, "CMS Report", startrow=row_count, startcol=0, index=False)
            df1.to_excel(writer, "CMS Report", startrow=row1, startcol=0, index=False)
            # print df, 'aaaa'

            workbook = writer.book
            worksheet = writer.sheets['CMS Report']
            workbook.formats[0].set_font_size(18)
            format1 = workbook.add_format(
                {'bg_color': '#0c50a0', 'font_color': '#FFFFFF', 'font_size': 20, 'text_wrap': 'true'})
            format4 = workbook.add_format({'font_name': 'Arial', 'font_size': 20, 'bold': True})
            merge_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'font_size': 25,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': 'white'
            })


            format1.set_align('center')

            if start and end:
                from_date = datetime.datetime.strptime(self.from_date, "%Y-%m-%d").strftime("%d-%m-%Y")
                to_date = datetime.datetime.strptime(self.to_date, "%Y-%m-%d").strftime("%d-%m-%Y")
                report_days = "Report From Date ({0}) - Till Date ({1})".format(from_date, to_date)
            else:
                from_date = None
                to_date = None
                report_days = None
            sub_tittle1 = 'A.Payment Details :'
            sub_tittle2 = 'B.Weighment Details :'
            ryot_no = "Ryot No :"
            season = "Season :"
            ryot_name = "Ryot Name :"
            address = "Address :"
            ryot_name1 = rec.ryot_name
            season1 = rec.season
            worksheet.merge_range('A1:F1', self.company_id.name, merge_format)
            worksheet.merge_range('A2:F2', self.company_id.partner_id.zip, merge_format)
            worksheet.merge_range('A3:F3', 'Ryot Payment Statement', merge_format)
            worksheet.merge_range('A4:F4', '', merge_format)
            worksheet.merge_range('A5:F5', report_days, merge_format)
            worksheet.write(row,0, sub_tittle1, format4)
            worksheet.write(row+1,0, ryot_no, format4)
            worksheet.write(row+1,1, ryot_number, format4)
            worksheet.write(row+2,0, ryot_name, format4)
            worksheet.write(row+2,1, ryot_name1, format4)
            worksheet.write(row+1,4, season, format4)
            worksheet.write(row+1,5, season1, format4)
            worksheet.write(row+2,4, address, format4)
            worksheet.write(row_count,0, 'Bill No', format1)
            worksheet.write(row_count,1, 'From date', format1)
            worksheet.write(row_count,2, 'To Date', format1)
            worksheet.write(row_count,3, 'Tonnes', format1)
            worksheet.write(row_count,4, 'Rate', format1)
            worksheet.write(row_count,5, 'Gross Amt', format1)

            worksheet.write(row1-1, 0, sub_tittle2, format4)
            worksheet.write(row1, 0, 'Date', format1)
            worksheet.write(row1, 1, 'Wmt No', format1)
            worksheet.write(row1, 2, 'Plot', format1)
            worksheet.write(row1, 3, 'Gross', format1)
            worksheet.write(row1, 4, 'Tare', format1)
            worksheet.write(row1, 5, 'Binder', format1)
            worksheet.write(row1, 6, 'Net', format1)
            worksheet.write(row1, 7, 'Gang Name', format1)
            worksheet.write(row_count+count_row+1, 0, 'Total', format4)
            worksheet.write(row_count+count_row+1, 3, tonnes, format4)
            worksheet.write(row_count+count_row+1, 5, gross_amount, format4)
            worksheet.write(row_count+count_row+1, 6, tnwf, format4)
            worksheet.write(row_count+count_row+1, 7, harvest_amount, format4)

            worksheet.write(row1+df1_count+1, 0, 'Total', format4)
            worksheet.write(row1+df1_count+1, 3, gross_weight, format4)
            worksheet.write(row1+df1_count+1, 4, tare_weight, format4)
            worksheet.write(row1+df1_count+1, 5, bind_qty, format4)
            worksheet.write(row1+df1_count+1, 6, net_weight, format4)
            worksheet.set_default_row(30)
            worksheet.set_column(0, 18, 18)
        writer.save()
        PREVIEW_PATH = '/tmp/Ryot_bill.xls'
        encoded_string = ""
        with open(PREVIEW_PATH, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        self.file_name = 'Ryot_bill.xls'
        self.file_output = encoded_string


# CMSReport()

class RyotBill(models.Model):
    _name = 'ryot.bill'
    _rec_name = 'ryot_number'

    season = fields.Char(string='Season', required=True)
    processid = fields.Char(string='Process ID', required=True)
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    ryot_number = fields.Char(string='Ryot number')
    ryot_name = fields.Char(string='Ryot Name')
    net_weight = fields.Float(string='Net weight')
    cane_price = fields.Float(string='Cane Price')
    gross_amount = fields.Float(string='Gross Amount')
    tnwf = fields.Float(string='TNWF')
    harvest_amount = fields.Float(string='Harvest Amount')
    material = fields.Float(string='Material')
    seed = fields.Float(string='Seed')
    service = fields.Char(string='Service')
    advance = fields.Float(string='Advance')
    bad_cane = fields.Float(string='Bad Cane')
    total_deductions = fields.Float(string='Total Deductions')
    net_pay = fields.Float(string='Netpay')
    bank = fields.Char(string='Bank')
    branch = fields.Char(string='Branch')
    account_no = fields.Char(string='Account No')
    payment_type = fields.Char(string='Payment Type')