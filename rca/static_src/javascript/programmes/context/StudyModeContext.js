import { createContext, useContext } from 'react';

export const StudyModeContext = createContext();

export const useStudyMode = () => useContext(StudyModeContext);
