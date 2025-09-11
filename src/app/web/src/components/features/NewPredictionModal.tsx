import { Dialog, Transition } from '@headlessui/react';
import React, { Fragment, useState } from 'react';
import PredictForm from '../../features/PredictForm/PredictForm';
import CSVUpload from '../../features/CSVUpload/CSVUpload';
import { XMarkIcon } from '@heroicons/react/24/solid';

export default function NewPredictionModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [mode, setMode] = React.useState<'single' | 'batch'>('single');
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center pt-12 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex items-center justify-between mb-4">
                  <Dialog.Title className="text-lg font-semibold">{mode === 'single' ? 'New Prediction' : 'Batch Predict via CSV'}</Dialog.Title>
                  <button onClick={onClose} className="text-slate-500 hover:text-slate-700"><XMarkIcon className="w-5 h-5" /></button>
                </div>
                {mode === 'single' ? (
                  <PredictForm onSuccess={() => onClose()} />
                ) : (
                  <CSVUpload onComplete={onClose} />
                )}

                <div className="mt-4 flex justify-end">
                  {mode === 'single' ? (
                    <button className="text-sm text-indigo-600 hover:underline" onClick={() => setMode('batch')}>Batch predict instead</button>
                  ) : (
                    <button className="text-sm text-indigo-600 hover:underline" onClick={() => setMode('single')}>Single Prediction</button>
                  )}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
} 