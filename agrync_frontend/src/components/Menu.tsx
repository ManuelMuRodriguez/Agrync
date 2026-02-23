import { Link, useLocation, useNavigate} from "react-router-dom";
import { LuLayoutDashboard } from "react-icons/lu";
import { VscGraphLine } from "react-icons/vsc";
import { IoSettingsOutline } from "react-icons/io5";
import { RiAdminLine } from "react-icons/ri";
import { RiLogoutBoxLine } from "react-icons/ri";
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { logout } from '../api/AuthAPI';
import { toast } from 'react-toastify';
import { Role } from "../types";
import { useTranslation } from 'react-i18next';


type MenuProps = {
    role: Role;
};

export default function Menu({role}: MenuProps) {

    const { t, i18n } = useTranslation();
    const queryClient = useQueryClient()
    const navigate = useNavigate()
    const location = useLocation()

    const tabs = [
        { name: t('menu.dashboard'), href: '/dashboard', icon: LuLayoutDashboard },
        { name: t('menu.graphs'), href: '/graficas', icon: VscGraphLine },
        { name: t('menu.configuration'), href: '/configuracion/perfil', icon: IoSettingsOutline },
        { name: t('menu.administration'), href: '/administracion/monitorizacion/modbus', icon: RiAdminLine },
    ];

    const {mutate} = useMutation({
    mutationFn: logout,
    onError: (error) => {
      toast.error(error.message, {
      closeButton: false,
      className: 'bg-error text-white'
      })
    },
    onSuccess: (data) => {
      localStorage.removeItem('ACCESS_TOKEN_AGRYNC')
      queryClient.invalidateQueries({ queryKey: ['userInfo'] })
      navigate("/login")
      toast.success(data, {
      closeButton: false,
      className: 'bg-right-green text-white'
      })
    }
    
  })


    const handleLogout = () => mutate()

    const handleLanguageToggle = () => {
        const newLang = i18n.language.startsWith('es') ? 'en' : 'es';
        i18n.changeLanguage(newLang);
    };

    //const queryClient = useQueryClient()
    //const logout = () => {
    //    localStorage.removeItem('ACCESS_TOKEN_AGRYNC')
    //    queryClient.invalidateQueries({queryKey: ['userInfo']})
    //}


  const filteredTabs = tabs.filter(tab => {
    if (tab.name === t('menu.administration') && role !== 'Administrador') {
      return false;
    }
    return true;
  });

  return (

    <nav className='h-fit flex flex-col items-center justify-between flex-grow ' >

        <div className=''>



        {filteredTabs.map((tab) => (
                            <Link
                                key={tab.href}
                                to={tab.href}
                                className={`${location.pathname.split("/")[1] == tab.href.split("/")[1] ? 'bg-bg-selection': 'hover:bg-bg-hover transition duration-300'} w-65 text-xl text-text-green font-semibold flex items-center justify-center rounded-2xl h-17 `}
                            >
                                <tab.icon
                                    className='mr-2'
                                    aria-hidden="true"
                                />
                                <span>{tab.name}</span>
                            </Link>
                        ))}


        </div>

        <div className='mb-4 flex flex-col items-center gap-2'>

            <button
                onClick={handleLanguageToggle}
                className='w-65 text-sm text-text-green font-semibold flex items-center justify-center rounded-lg h-10 hover:bg-bg-hover transition duration-300 border border-gap'
                title={t('common.language')}
            >
                {i18n.language.startsWith('es') ? '🇬🇧 EN' : '🇪🇸 ES'}
            </button>

            <button
                key="cerrar-sesion"
                className=' w-65 text-xl text-text-green font-semibold flex items-center justify-center rounded-lg h-17  hover:bg-bg-hover transition duration-300'
                onClick={handleLogout}
            > <RiLogoutBoxLine className='mr-2'
            aria-hidden="true" />  {t('menu.logout')}</button>

        </div>

    </nav>
  )
}
