import datetime
from .colors import color


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def get_up_time(started_at: str):
    up_time = (
            datetime.datetime.now()
            - datetime.datetime.fromisoformat(started_at)
    )
    return str(chop_microseconds(up_time))


def format_report(report: dict, app_name: str = None) -> str:
    """
    Arguments:
        app_name: installation name.
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
    if app_name:
        result += f'Installation: {app_name}\n'
    header = ('Name', 'State', 'Pid', 'Port', 'Uptime', 'ErrorCode')
    template = '{:<20}' * 2 + '{:<10}' * (len(header) - 2) + '\n'
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

        error_code = ''
        if service_info['system_data']['error_code'] is not None:
            error_code = service_info['system_data']['error_code']

        port = ''
        if service_info['service_data']['port']:
            port = service_info['service_data']['port']

        started_at = service_info['system_data']['started_at']

        uptime = ''
        if started_at is not None and started_at != 'None':
            uptime = get_up_time(started_at)

        row = (name, state, pid, port, uptime, error_code)
        if service_info['init_config']['service']:
            services.append(row)
        else:
            workers.append(row)

    for p_name, p_array in (
            ('Services', services),
            ('Workers', workers)
    ):
        if p_array:
            header_row = [f'{color.bold}{p_name}{color.end}', *['' for _ in range(len(header) - 1)]]
            result += template.format(*header_row)
        for process in p_array:
            result += template.format(
                *[
                    str(x)
                    for x in process
                ]
            )

    return result


def format_logs_response(logs_response: dict, app_name: str = None) -> str:
    if not logs_response:
        return f"No logs found for {app_name}."

    colors = [color.white, color.green, color.blue, color.cyan, color.magenta]

    result = f"Installation: {app_name}\n"

    for i, (service_name, service_logs) in enumerate(logs_response.items()):
        result += colors[i % len(colors)]
        result += service_name + '\n'
        if service_logs.strip():
            result += service_logs
            result += '\n'
        else:
            result += 'No logs found.\n'
        result += color.end

    return result
