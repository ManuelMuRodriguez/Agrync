import { z } from 'zod'

/* Auth */
const authSchema = z.object({
    email: z.string().email(),
    username: z.string().email(),
    password: z.string(),
    password_confirmation: z.string()
})

type Auth = z.infer<typeof authSchema>
export type UserLoginForm = Pick<Auth, 'username' | 'password'>
export type CreatePasswordForm = Pick<Auth, 'email' | 'password' | 'password_confirmation'>

const Role = z.enum(['Administrador','Lector','Editor'])

export type Role = z.infer<typeof Role>

export const roleOptions = Role.options;


/* User */
export const userSchema = authSchema.pick({
    email: true,
    password: true
}).extend({
    role: Role,
    full_name: z.string(),
    id: z.string()
})
export type User = z.infer<typeof userSchema>
export type UserNameForm = Pick<User, 'full_name'>

export const userInfoSchema = userSchema.pick({
  full_name: true,
  role: true,
  id: true
})



const userTable = userSchema.pick({
  email: true,
  role: true,
  id: true,
  full_name: true,


}).extend({
  active: z.boolean(),
  createdAt: z.string(),
  updatedAt: z.string()

})

export type UserTable = z.infer<typeof userTable>

export const usersTableResponseSchema = z.object({
    data: z.array(userTable),
    totalRowCount: z.number()
})

export type UsersTableResponse = z.infer<typeof usersTableResponseSchema>



const showUserTable = userTable.pick({
  email: true,
  role: true,
  id: true,
  full_name: true,
  createdAt: true,
  updatedAt: true

}).extend({
  active: z.string()

})
export type ShowUserTable = z.infer<typeof showUserTable>




/* Cambiar password */
export const passwordUpdateSchema = userSchema.pick({
    password: true
}).extend({
    new_password: z.string(),
    new_password_confirmation: z.string()
})
export type ChangePasswordForm = z.infer<typeof passwordUpdateSchema>


/* Cambiar email */
export const emailUpdateSchema = userSchema.pick({
    email: true
}).extend({
    new_email: z.string().email(),
    new_email_confirmation: z.string().email()
})
export type ChangeEmailForm = z.infer<typeof emailUpdateSchema>



/* Generic Device */

const DeviceType = z.enum(["Modbus"])

const InputOPC = z.enum(['Int16','UInt16','Int32','UInt32','Int64','UInt64','Float32','Float64'])

type InputOPC = z.infer<typeof InputOPC>

export const opcTypes = InputOPC.options;

const variableAtributesSchema = z.object({
  name: z.string(),
  type: InputOPC,
  scaling: z.number().nullable(),
  writable: z.boolean(),
  min_value: z.number().nullable(),
  max_value: z.number().nullable(),
  unit: z.string().nullable(),
  decimals: z.number().int()
});


export const genericDeviceSchema = z.object({
    name: z.string(),
    type: DeviceType,
    variables: z.array(variableAtributesSchema).optional()
})

export const genericDevicesSchema = z.array(
    genericDeviceSchema
)


export type GenericDevice = z.infer<typeof genericDeviceSchema>

export type VariableAtributes = z.infer<typeof variableAtributesSchema>;

export type GenericDevices = z.infer<typeof genericDevicesSchema>

/* Devices (str) User */

export const onlyNamesDevicesSchema = z.array(z.string());

export const devicesDragDrop = z.object({
    name: z.string(),
    id:z.string()
})

export type DevicesDragDrop = z.infer<typeof devicesDragDrop>

export const sendDeviceNamesSchema = z.object({
  names: z.array(z.string())
})
export type SendDeviceNames = z.infer<typeof sendDeviceNamesSchema>


/* Historical */
export const genericDevicesNamesSchema = z.array(
    z.object({
        name: z.string(),
        variables_names: z.array(z.string())
    })
)


export type GenericDevicesNames = z.infer<typeof genericDevicesNamesSchema>;


const Aggregation = z.enum(['sin','horas','dias'])


export const formGraficas = z.object({
  variables_names: z.array(z.string()).optional().default([]),
  start_date: z.date().nullable(),
  end_date: z.date().nullable(),
  aggregation: Aggregation
});

export type FormGraficas = z.infer<typeof formGraficas>;



export const historicalDataSchema = z.array(z.object({
  name: z.string(),
  series: z.array(z.object({
      timestamp: z.string(),
      value: z.number()
  }))  
}));

export type HistoricalData = z.infer<typeof historicalDataSchema>;






/* Last-Values */


export type FormDashboard = Pick<FormGraficas, 'variables_names'>


export const lastDataSchema = z.array(z.object({
  name: z.string(),
  value: z.number().nullable(),
  timestamp: z.string().nullable()
}));


export type LastData = z.infer<typeof lastDataSchema>;


const lastDataCard = z.object({
  value: z.number().nullable(),
  timestamp: z.string().nullable()
});

export type LastDataCard = z.infer<typeof lastDataCard>;



/* Write-Value */


const writeValue = z.object({
  value: z.number().nullable()
});

export type FormWriteValue = z.infer<typeof writeValue>;


export const sendValueOPC = writeValue.pick({
    value: true
}).extend({
    deviceType: DeviceType,
    nameVariable: z.string(),
    nameGenericDevice: z.string(),
})


export type SendValueOPC = z.infer<typeof sendValueOPC>;





/* Modbus */


const modbusDeviceTable = z.object({
  name: z.string(),
  ip: z.string().ip({ version: "v4" }),
  createdAt: z.string(),
  updatedAt: z.string(),
  id:z.string()
})

export type ModbusDeviceTable = z.infer<typeof modbusDeviceTable>

export const modbusDeviceTableResponseSchema = z.object({
    data: z.array(modbusDeviceTable),
    totalRowCount: z.number()
})

export type ModbusDeviceTableResponse = z.infer<typeof modbusDeviceTableResponseSchema>




const modbusSlaveTable = modbusDeviceTable.pick({
  createdAt: true,
  updatedAt: true,
  id: true,
  name: true
}).extend({
    slave_id: z.number(),
    name_device: z.string(),
    id_device: z.string()
})

const modbusDevicesAvailable = modbusDeviceTable.pick({
  id: true,
  name: true
})


export type ModbusSlaveTable = z.infer<typeof modbusSlaveTable>

export const modbusSlaveTableResponseSchema = z.object({
    data: z.array(modbusSlaveTable),
    totalRowCount: z.number(),
    devicesAvailable: z.array(modbusDevicesAvailable)
})

export type ModbusSlaveTableResponse = z.infer<typeof modbusSlaveTableResponseSchema>






const Endian = z.enum(['Little','Big'])

type Endian = z.infer<typeof Endian>

export const endianOptions = Endian.options;


const modbusVariableTable = modbusSlaveTable.pick({
  createdAt: true,
  updatedAt: true,
  id: true,
  name: true,
  name_device: true
}).extend({
  name_slave: z.string(),
  type: InputOPC,
  address: z.number(),
  scaling: z.number().nullable(),
  decimals: z.number().nullable(),
  endian: Endian.nullable(),
  interval: z.number().int().nullable(),
  length: z.number().int().nullable(),
  writable: z.boolean().nullable(),
  min_value: z.number().nullable(),
  max_value: z.number().nullable(),
  unit: z.string().nullable(),
  id_db_slave: z.string(),
  id_db_device: z.string(),
  id_device_slave: z.string().optional()
})


const modbusDevicesSlavesAvailable = modbusVariableTable.pick({
  id_db_slave: true,
  id_db_device: true,
  name_device: true,
  name_slave: true
})




export type ModbusVariableTable = z.infer<typeof modbusVariableTable>

export const modbusVariableTableResponseSchema = z.object({
    data: z.array(modbusVariableTable),
    totalRowCount: z.number(),
    devicesSlavesAvailable: z.array(modbusDevicesSlavesAvailable)
})

export type ModbusVariableTableResponse = z.infer<typeof modbusVariableTableResponseSchema>


const TaskState = z.enum(['running','stopped', 'failed'])


export const taskSchema = z.object({
    state: TaskState,
    locked: z.boolean()
})

export type Task = z.infer<typeof taskSchema>

