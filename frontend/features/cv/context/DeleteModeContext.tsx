"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface DeleteModeContextType {
  skipConfirmation: boolean;
  setSkipConfirmation: (value: boolean) => void;
  resetConfirmation: () => void;
}

const DeleteModeContext = createContext<DeleteModeContextType | undefined>(
  undefined
);

interface DeleteModeProviderProps {
  children: ReactNode;
}

export function DeleteModeProvider({ children }: DeleteModeProviderProps) {
  const [skipConfirmation, setSkipConfirmation] = useState(false);

  const resetConfirmation = () => {
    setSkipConfirmation(false);
  };

  return (
    <DeleteModeContext.Provider
      value={{
        skipConfirmation,
        setSkipConfirmation,
        resetConfirmation,
      }}
    >
      {children}
    </DeleteModeContext.Provider>
  );
}

export function useDeleteMode() {
  const context = useContext(DeleteModeContext);
  if (context === undefined) {
    throw new Error("useDeleteMode must be used within a DeleteModeProvider");
  }
  return context;
}
