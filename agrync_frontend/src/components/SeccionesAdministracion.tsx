import { Link, useLocation } from 'react-router-dom'
import { MdOutlineMonitor } from "react-icons/md";
import { IoRadio } from "react-icons/io5";
import { FaUsersCog } from "react-icons/fa";

const tabs = [
    {name: 'Monitoring', href: '/administracion/monitorizacion/modbus', icon: MdOutlineMonitor, key: 'monitorizacion'},
    {name: 'Devices', href: '/administracion/dispositivos/modbus', icon: IoRadio, key: 'dispositivos'},
    {name: 'Users', href: '/administracion/usuarios', icon: FaUsersCog, key: 'usuarios'}
]

export default function SeccionesAdministracion() {
    const location = useLocation()
    const pathSection = location.pathname.split('/')[2]
    
    return (
        <div className='-mt-8 -ml-5 mb-10 w-fit sticky top-0 bg-white pl-5 pt-8 z-20'>
            <div className="block">
                <div className="border-b border-gap ">
                    <nav className="flex" aria-label="Tabs">
                        {tabs.map((tab) => (
                            <Link
                                key={tab.name}
                                to={tab.href}
                                className= {`${tab.key === pathSection? 'border-text-green text-text-green' : 'border-transparent text-gap hover:border-button-cancel-hover hover:text-button-cancel-hover'} group inline-flex items-center border-b-2 py-4 px-16 text-3xl font-semibold`}
                                
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