import { json } from '@codemirror/lang-json';
import { useColorMode } from '@chakra-ui/react';
import  ReactCodeMirror, { ReactCodeMirrorProps } from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { useCallback } from 'react';
import * as React from 'react';


export type Mode = 'python' | 'json';


interface CodeEditorProps extends ReactCodeMirrorProps {
    mode?: Mode;
  }

export function CodeEditor({ mode = 'json', ...rest }: CodeEditorProps) {
    const { colorMode } = useColorMode();
    console.log("MOOOOODE:::: ", mode)
    const getLanguage = useCallback(() => {
      switch (mode) {
        case 'python':
          return python();
        case 'json':
          return json();
      }
      }, [mode]);
  
    return <ReactCodeMirror theme={colorMode} height="500px" width="100%" extensions={[getLanguage()]} {...rest} />;
  }
  