import { useLocation, useNavigate } from 'react-router-dom'


const options = [
    {name: 'Modbus', href: 'modbus'}
]


export default function SeleccionComunicacion() {
    const navigate = useNavigate()
    const location = useLocation()
    const currentTab = options.filter(option => option.href === location.pathname.split("/").filter(Boolean).pop())[0].href


    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newValue = e.target.value;
    
        const currentPath = window.location.pathname;
     
        const pathSegments = currentPath.split("/");
    
        pathSegments[pathSegments.length - 1] = newValue;
    
        const newPath = pathSegments.join("/");
    
        navigate(newPath);

    };

  return (
    <>
                <select
                    id="tabs"
                    name="tabs"
                    className="block w-1/3 rounded-md border-gap focus:border-button focus:ring-button font-medium text-2xl"
                    onChange={ handleChange }
                    value={currentTab}
                >
                    {options.map((option) => {
                        return (
                            <option className='font-medium'
                                value={option.href}
                                key={option.name}>{option.name}</option>
                        )
                    })}
                </select>
    </>
  )
}