import { Dialog, Transition } from '@headlessui/react';
import { Fragment, useEffect, useState } from 'react';
import {
    DndContext,
    DragOverlay,
    pointerWithin,
    PointerSensor,
    useDraggable,
    useDroppable,
    useSensor,
    useSensors,
    type DragStartEvent,
    type DragOverEvent,

} from '@dnd-kit/core';
import { FaArrowsLeftRight } from "react-icons/fa6";

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAvailableDevices, getUserDevices, updateUserDevices } from '../api/UserAPI';
import { DevicesDragDrop, User } from '../types';
import { toast } from 'react-toastify';

function DraggableItem({ id, name }: DevicesDragDrop) {
    const { attributes, listeners, setNodeRef } = useDraggable({ id });

    return (
        <div
            ref={setNodeRef}
            {...attributes}
            {...listeners}
            className="bg-white border-l-4 text-center text-button px-4 py-2 rounded cursor-move hover:bg-bg-hover"
        >
            {name}
        </div>
    );
}

function DroppableColumn({
    id,
    title,
    items,
}: {
    id: string;
    title: string;
    items: DevicesDragDrop[];
}) {
    const { setNodeRef, isOver } = useDroppable({ id });

    return (
        <div>
            <h2 className="text-3xl border-2 border-title-draggable font-bold text-button p-2 text-center">{title}</h2>
            <div
                ref={setNodeRef}
                className={`space-y-2 min-h-[200px] p-3 rounded transition-colors ${isOver ? 'bg-bg-section-outline' : 'bg-bg-selection-dropdown'
                    }`}
            >
                {items.map((device) => (
                    <DraggableItem key={device.id} id={device.id} name={device.name} />
                ))}
            </div>
        </div>
    );
}

type ModifyUserDevicesProps = {
    isModalOpen: boolean;
    setIsModalOpen: React.Dispatch<React.SetStateAction<boolean>>;
    userId: User['id'];
};

export default function ModificarDispositivosUsuario({
    isModalOpen,
    setIsModalOpen,
    userId,
}: ModifyUserDevicesProps) {
    const queryClient = useQueryClient();

    const [assigned, setAssigned] = useState<DevicesDragDrop[]>([]);
    const [available, setAvailable] = useState<DevicesDragDrop[]>([]);
    const [activeId, setActiveId] = useState<string | null>(null);

    const { data: assignedData } = useQuery({
        queryKey: ['userDevices', userId],
        queryFn: () => getUserDevices({ userId }),
        enabled: isModalOpen,
        retry: false,
        refetchOnWindowFocus: false,
    });

    const { data: availableData } = useQuery({
        queryKey: ['availableDevices', userId],
        queryFn: () => getAvailableDevices({ userId }),
        enabled: isModalOpen,
        retry: false,
        refetchOnWindowFocus: false,
    });

    useEffect(() => {
        if (assignedData) {
            const mappedAssigned = assignedData.map((id) => ({ id, name: id }));
            setAssigned(mappedAssigned);
        }
        if (availableData) {
            const mappedAvailable = availableData.map((id) => ({ id, name: id }));
            setAvailable(mappedAvailable);
        }
    }, [assignedData, availableData]);

    const updateMutation = useMutation({
        mutationFn: updateUserDevices,
        onError: (error) => {
            toast.error(error.message, {
                closeButton: false,
                className: 'bg-error text-white'
            })
        },
        onSuccess: (data) => {
            toast.success(data, {
                closeButton: false,
                className: 'bg-right-green text-white'
            })
            queryClient.invalidateQueries({ queryKey: ['tableUsers'] });
        },
    });

    const handleModalClose = () => {
        const deviceIds = assigned.map((d) => d.id);
        updateMutation.mutate({ formData: { names: deviceIds }, userId });
        setIsModalOpen(false);
    };

    const sensors = useSensors(useSensor(PointerSensor));

    const handleDragStart = (event: DragStartEvent) => {
        setActiveId(event.active.id as string);
    };

    const handleDragOver = (event: DragOverEvent) => {
        const { active, over } = event;
        if (!over || active.id === over.id) return;

        const item = [...assigned, ...available].find((i) => i.id === active.id);
        if (!item) return;

        const isInAssigned = assigned.some((i) => i.id === active.id);
        const isInAvailable = available.some((i) => i.id === active.id);

        if (over.id === 'assigned' && isInAvailable) {
            setAvailable((prev) => prev.filter((i) => i.id !== active.id));
            setAssigned((prev) => [...prev, item]);
        } else if (over.id === 'available' && isInAssigned) {
            setAssigned((prev) => prev.filter((i) => i.id !== active.id));
            setAvailable((prev) => [...prev, item]);
        }
    };

    const handleDragEnd = () => {
        setActiveId(null);
    };


    return (
        <Transition show={isModalOpen} as={Fragment} appear>
            <Dialog
                as="div"
                className="relative z-40"
                onClose={() => setIsModalOpen(false)}
            >
                <Transition
                    show={isModalOpen}
                    as={Fragment}
                    enter="ease-out duration-300"
                    enterFrom="opacity-0"
                    enterTo="opacity-100"
                    leave="ease-in duration-200"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                >
                    <div className="fixed inset-0 bg-bg-modal" />
                </Transition>

                <div className="fixed inset-0 overflow-y-auto">
                    <div className="flex min-h-full items-center justify-center p-4 pt-12 text-center">
                        <Transition
                            show={isModalOpen}
                            as={Fragment}
                            enter="ease-out duration-300"
                            enterFrom="opacity-0 scale-95"
                            enterTo="opacity-100 scale-100"
                            leave="ease-in duration-200"
                            leaveFrom="opacity-100 scale-100"
                            leaveTo="opacity-0 scale-95"
                        >
                            <div className="relative transform overflow-hidden rounded-lg bg-white px-6 pb-4 text-left shadow-xl transition-all w-10/12 max-w-4xl">
                                <div className="flex justify-end p-2">
                                    <button
                                        onClick={handleModalClose}
                                        className="text-button-cancel-card hover:text-button-cancel-hover text-3xl font-bold cursor-pointer"
                                        aria-label="Cerrar modal"
                                    >
                                        ×
                                    </button>
                                </div>

                                <DndContext
                                    sensors={sensors}
                                    collisionDetection={pointerWithin}
                                    onDragStart={handleDragStart}
                                    onDragOver={handleDragOver}
                                    onDragEnd={handleDragEnd}
                                >
                                    <div className="flex flex-col md:flex-row items-stretch gap-6">
                                        <div className="flex-1">
                                            <DroppableColumn id="available" title="Available" items={available} />
                                        </div>

                                        <div className="w-full md:w-12 flex items-center justify-center">
                                            <FaArrowsLeftRight className="text-button text-2xl" />
                                        </div>

                                        <div className="flex-1">
                                            <DroppableColumn id="assigned" title="Assigned" items={assigned} />
                                        </div>
                                    </div>

                                    <DragOverlay>
                                        {activeId ? (
                                            <DraggableItem
                                                id={activeId}
                                                name={
                                                    [...available, ...assigned].find((i) => i.id === activeId)?.name || ''
                                                }
                                            />
                                        ) : null}
                                    </DragOverlay>
                                </DndContext>
                            </div>
                        </Transition>
                    </div>
                </div>
            </Dialog>
        </Transition>
    );


}
