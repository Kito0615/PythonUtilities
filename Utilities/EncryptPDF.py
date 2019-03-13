#! /usr/bin/env python3
# -*- coding:utf-8 -*-

from PyPDF2 import PdfFileReader, PdfFileWriter
import getopt
import sys
import os


def show_usage():
    print('-' * 75)
    print('Usage : %s [-h|-f|-p|-o][--help|--file|--password|--output] args')
    print('    -h, --help\t\t\tShow this help info.')
    print('    -f, --file PATH\t\tPATH to the pdf file to be encrypted.')
    print('    -p, --password PWD\tPassword to use to encrypt the file.')
    print('    -o, --output PATH\tOutput file path. Default same with input.')


def get_default_output(input_file):
    temp = input_file.split('.')[:-1]
    temp.append('encrypted')
    temp.append('pdf')
    return '.'.join(temp)


def format_path(p):
    return os.path.expanduser(p)


def open_output_path(op):
    os.system('open ' + op)


def encrypt_pdf(in_file, pwd, out_file):
    pdf_file = open(in_file, 'rb')
    pdf_reader = PdfFileReader(pdf_file)
    pdf_writer = PdfFileWriter()

    for page in range(pdf_reader.numPages):
        pdf_writer.addPage(pdf_reader.getPage(page))

    pdf_writer.encrypt(pwd)
    output_pdf = open(out_file, 'wb')
    pdf_writer.write(output_pdf)
    output_pdf.close()


def main():
    ops, args = getopt.getopt(sys.argv[1:], 'hf:p:o:', ['help', 'file=', 'password=', 'output='])
    input_pdf_file = ''
    input_password = ''
    output_pdf_file = ''
    for opt, arg in ops:
        if opt in ('-h', '--help'):
            show_usage()
            sys.exit()
        if opt in ('-f', '--file'):
            input_pdf_file = format_path(arg)
        if opt in ('-p', '--password'):
            input_password = arg
        if opt in ('-o', '--output'):
            output_pdf_file = format_path(arg)

    if len(input_pdf_file) == 0:
        show_usage()
        sys.exit(-1)

    if len(input_password) == 0:
        show_usage()
        sys.exit(-1)

    if len(output_pdf_file) == 0:
        output_pdf_file = get_default_output(input_pdf_file)

    encrypt_pdf(input_pdf_file, input_password, output_pdf_file)
    temp = output_pdf_file.split('/')[:-1]
    open_output_path('/'.join(temp))


if __name__ == '__main__':
    main()
