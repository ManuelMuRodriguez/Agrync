import { BrowserRouter, Routes, Route, Navigate } from 'react-router'
import EsqueletoWeb from './layouts/WebLayout'
import Dashboard from './pages/Dashboard'
import Graficas from './pages/Charts'
import EsqueletoConfiguracion from './layouts/ConfigLayout'
import EsqueletoAuth from './layouts/AuthLayout'
import Login from './pages/Login'
import CrearPassword from './pages/CreatePassword'
import Perfil from './pages/Profile'
import Credenciales from './pages/Credentials'
import EsqueletoAdministracion from './layouts/AdminLayout'
import Usuarios from './pages/Users'
import {  MantineProvider } from '@mantine/core';

import "./index.css";
import { ModalsProvider } from '@mantine/modals'
import EsqueletoMonitorizacion from './layouts/MonitoringLayout'
import ModbusMonitorizacion from './pages/ModbusMonitoring'
import EsqueletoDispositivos from './layouts/DevicesLayout'
import ModbusDispositivos from './pages/ModbusDevices'
import ServerOPCMonitorizacion from './pages/ServerOPCMonitoring'
import OPCtoFIWAREMonitorizacion from './pages/OPCtoFIWAREMonitoring'

function App() {

    return (

        <MantineProvider 
        theme={{
        fontFamily: 'Inter, sans-serif',
        headings: { fontFamily: 'Inter, sans-serif' },
      }}
      >{
        <ModalsProvider>
        <BrowserRouter>
            <Routes>
                <Route element={<EsqueletoAuth />}>
                    <Route path='login' element={<Login />} index/>
                    <Route path='crear-password' element={<CrearPassword />} />
                </Route>
                <Route element={<EsqueletoWeb />}>
                    <Route path='dashboard' element={<Dashboard />} />
                    <Route path='graficas' element={<Graficas />} />
                    <Route path= 'configuracion' element={<EsqueletoConfiguracion />}>
                        <Route path='perfil' element={<Perfil />} />
                        <Route path='credenciales' element={<Credenciales />} />
                    </Route>
                    <Route path='administracion' element={<EsqueletoAdministracion />}>
                        <Route path='monitorizacion' element={<EsqueletoMonitorizacion />} >
                            <Route path='modbus' element={<ModbusMonitorizacion />} />
                            <Route path='serverOPC' element={<ServerOPCMonitorizacion />} />
                            <Route path='OPCtoFIWARE' element={<OPCtoFIWAREMonitorizacion />} />
                        </Route>
                        <Route path='dispositivos' element={<EsqueletoDispositivos />} >
                            <Route path='modbus' element={<ModbusDispositivos />} />
                        </Route>
                        <Route path='usuarios' element={<Usuarios />} />
                    </Route>
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Route>
            </Routes>
        </BrowserRouter>
        </ModalsProvider>
}
        </MantineProvider>



    )


}



export default App