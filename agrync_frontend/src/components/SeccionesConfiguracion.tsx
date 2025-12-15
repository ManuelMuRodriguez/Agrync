import { Link, useLocation } from 'react-router-dom'
import { CgProfile } from "react-icons/cg";
import { TbLockPassword } from "react-icons/tb";

const tabs = [
    {name: 'User profile', href: '/configuracion/perfil', icon: CgProfile},
    {name: 'Credentials', href: '/configuracion/credenciales', icon: TbLockPassword}
]

export default function SeccionesConfiguracion() {
    const location = useLocation()
    
    return (
        <div className='-mt-8 mb-10 w-fit sticky top-0 bg-white pt-8'>
            <div className="block">
                <div className="border-b border-gap ">
                    <nav className="flex" aria-label="Tabs">
                        {tabs.map((tab) => (
                            <Link
                                key={tab.name}
                                to={tab.href}
                                className= {`${location.pathname === tab.href ? 'border-text-green text-text-green' : 'border-transparent text-gap hover:border-button-cancel-hover hover:text-button-cancel-hover'} group inline-flex items-center border-b-2 py-4 px-16 text-3xl font-semibold`}
                                
                            >
                                <tab.icon
                                    className='mr-2'
                                    aria-hidden="true"
                                />
                                <span>{tab.name}</span>
                            </Link>
                        ))}
                    </nav>
                </div>
            </div>
        </div>
    )
}