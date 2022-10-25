import datetime


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def get_up_time(started_at: str):
    up_time = (
            datetime.datetime.now()
            - datetime.datetime.fromisoformat(started_at)
    )
    return str(chop_microseconds(up_time))


def format_report(report: dict) -> str:
    """
    Arguments:
        report: dictionary returned by status command
            format: {<service_name>: <service_info>}

    Report Format:

        Name             State                  Pid   Port    Uptime
        Services
          kanban         started                120   9301    00:23:54
          tenants        stopped                121   9302    00:03:21
        Workers
          get_cdr        failed_starting_loop   122
          get_sim_info   started                123           00:23:41
    """
    result = ''
    template = '{:<15}|{:<15}|{:<15}|{:<15}|{:<15}\n'
    header = ('Name', 'State', 'Pid', 'Port', 'Uptime')
    workers = []
    services = []
    if report is None:
        return 'No report found.'
    
    result += template.format(*header)
    for service_name, service_info in report.items():
        name = service_name
        state = service_info['system_data']['state']
        pid = ''
        if service_info['system_data']['error_code'] is None:
            pid = service_info['system_data']['pid']
        port = service_info['service_data']['port']
        started_at = service_info['system_data']['started_at']
        uptime = ''
        if started_at is not None and started_at != 'None':
            uptime = get_up_time(started_at)
        if service_info['init_config']['service']:
            services.append(
                (name, state, pid, port, uptime)
            )
        else:
            workers.append(
                (name, state, pid, '', uptime)
            )

    for p_name, p_array in (
            ('Services', services),
            ('Workers', workers)
    ):
        if p_array:
            result += template.format(*(p_name, '', '', '', ''))
        for process in p_array:
            result += template.format(*process)

    return result
