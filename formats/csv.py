def csv(data, report_config, description, output):
    """

    Output report in csv

    :param data: data collection for report
    :type data: list
    :param report_config: report configuration
    :type report_config: dict
    :param description: fields description
    :type description: tuple
    :param output: output file name
    :type output: str

    """
    with open(output, 'w') as f:
        description_string = ''
        for column_name in description:
            description_string += '%s%s' % (column_name[0], report_config.get('field_delimiter', ';'))
        f.write(description_string[:-1])
        f.write('\n')
        for row in data:
            data_string = ''
            for column in row:
                data_string += '%s%s' % (column, report_config.get('field_delimiter', ';'))
            f.write(data_string[:-1])
            f.write('\n')
    f.close()
