import {
  Box,
  Button,
  Input,
  Select,
  Stack,
  Text,
  Textarea,
} from "@chakra-ui/react";
import { useCompositeState } from "ds4biz-core";
import { useContext } from "react";
import { StateContext } from "../../config/constants";

export function PredBaseForm({ onSubmit }) {
  const state = useCompositeState({
    name: "",
    tag: "",
  });
  const _state = useContext(StateContext);
  return (
    <Stack>
       <Text fontSize="xs">
        Name
        <Box as="span" color="red">
          *
        </Box>
      </Text>
      <Input
        value={state.name}
        onChange={(e) => (state.name = e.target.value)}
        type="text"
        isInvalid={state.name === ""}
      />
    
      <Text fontSize="xs">Model Tag</Text>
      <Textarea
        value={state.tag}
        onChange={(e) => (state.tag = e.target.value)}
      />

      <Text fontSize="xs">Pretrained Model</Text>
      <Select
        value={state.pretrained_model}
        onChange={(e) => (state.pretrained_model = e.target.value)}
      >
        <option></option>
        {_state.predictors.map((el) => (
          <option key={el}>{el}</option>
        ))}
      </Select>
      <Button
        onClick={(e) => {
          onSubmit(
            state.name,
            state.tag,
            state.pretrained_model,
          );
        }}
      >
        Create
      </Button>
    </Stack>
  );
}

