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
    
        // Get current URL path
        const currentPath = window.location.pathname;
     
        // Split the URL into segments
        const pathSegments = currentPath.split("/");
    
        // Replace the last segment with the new value
        pathSegments[pathSegments.length - 1] = newValue;
    
        // Join segments and update the URL
        const newPath = pathSegments.join("/");
    
        // Navigate to the new URL
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