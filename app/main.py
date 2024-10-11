import os
from tempfile import TemporaryDirectory
import traceback
from functions import Oi_Process
from Objects.Obj_ApiSpring import LoginError, get_logins, send_log


def main():
    current_dir = os.path.dirname(__file__)
    ambient = 'hml'
    logins = get_logins('OI', 'hml')

    for login in logins:
        print(f'\n|{"="*60}|')
        print(login)
        tries = 3
        for try_num in range(tries):
            with TemporaryDirectory(prefix='oi_', dir=current_dir) as oi_path:
                try:
                    Oi_Process(login, oi_path)

                except LoginError as e:
                    print(e)
                    tb = traceback.format_exc()
                    send_log(
                        ambient=ambient,
                        title=f'Erro nas credenciais do cliente {login.cliente_id}',
                        message=str(e),
                        stacktrace=tb,
                        origin='Automação OI Fixa-Dados',
                        status='error',
                        cliente_adm_id=login.cliente_id
                    )
                    break

                except Exception as e:
                    print(e)
                    if try_num == tries - 1:
                        send_log(
                            ambient=ambient,
                            title=f'Erro de processo do cliente {login.cliente_id}',
                            message=str(e),
                            stacktrace=tb,
                            origin='Automação OI Fixa-Dados',
                            status='error',
                            cliente_adm_id=login.cliente_id
                        )

                else:
                    send_log(
                        ambient=ambient,
                        title=f'Download concluído com sucesso do cliente {login.cliente_id}',
                        message='',
                        stacktrace='',
                        origin='Automação OI Fixa-Dados',
                        status='success',
                        cliente_adm_id=login.cliente_id
                    )
                    break


# Main function execution starts here
if __name__ == "__main__":
    main()
