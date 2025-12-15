import { BrowserRouter, Routes, Route, Navigate } from 'react-router'
import EsqueletoWeb from './layouts/EsqueletoWeb'
import Dashboard from './pages/Dashboard'
import Graficas from './pages/Graficas'
import EsqueletoConfiguracion from './layouts/EsqueletoConfiguracion'
import EsqueletoAuth from './layouts/EsqueletoAuth'
import Login from './pages/Login'
import CrearPassword from './pages/CrearPassword'
import Perfil from './pages/Perfil'
import Credenciales from './pages/Credenciales'
import EsqueletoAdministracion from './layouts/EsqueletoAdministracion'
import Usuarios from './pages/Usuarios'
import {  MantineProvider } from '@mantine/core';

import "./index.css";
import { ModalsProvider } from '@mantine/modals'
import EsqueletoMonitorizacion from './layouts/EsqueletoMonitorizacion'
import ModbusMonitorizacion from './pages/ModbusMonitorizacion'
import EsqueletoDispositivos from './layouts/EsqueletoDispositivos'
import ModbusDispositivos from './pages/ModbusDispositivos'
import ServerOPCMonitorizacion from './pages/ServerOPCMonitorizacion'
import OPCtoFIWAREMonitorizacion from './pages/OPCtoFIWAREMonitorizacion'

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