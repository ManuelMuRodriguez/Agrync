import { useLocation, useNavigate } from 'react-router-dom'


const options = [
    {name: 'Modbus', href: 'modbus'},
    {name: 'ServerOPC', href: 'serverOPC'},
    {name: 'OPCtoFIWARE', href: 'OPCtoFIWARE'}
]


export default function SeleccionTask() {
    const navigate = useNavigate()
    const location = useLocation()
    const currentTab = options.filter(option => option.href === location.pathname.split("/").filter(Boolean).pop())[0].href


    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newValue = e.target.value;
    
        // Obtener la URL actual
        const currentPath = window.location.pathname;
     
        // Dividir la URL en segmentos
        const pathSegments = currentPath.split("/");
    
        // Reemplazar el último segmento con el nuevo valor
        pathSegments[pathSegments.length - 1] = newValue;
    
        // Unir los segmentos y actualizar la URL
        const newPath = pathSegments.join("/");
    
        // Navegar a la nueva URL
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