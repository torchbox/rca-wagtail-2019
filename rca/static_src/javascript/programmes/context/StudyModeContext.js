import React, { createContext, useContext, useState } from 'react';

export const StudyModeContext = createContext();

export const useStudyMode = () => useContext(StudyModeContext);
