import { Button, Flex, HStack, Stack } from "@chakra-ui/react";
import { useCompositeState } from "ds4biz-core";
import { useContext } from "react";
import { CLIENT, StateContext } from "../../config/constants";
import { Model } from "./Model";
import { ModelCreation } from "./ModelCreation";
import { RiAddFill } from 'react-icons/ri';
import { ModelDetails } from "./ModelDetails";



export function Models({ models }) {
  const state = useCompositeState({ view: "list" });
  const _state = useContext(StateContext);
  switch (state.view) {
    case "list":
      return (
        <Stack w="100%" h="100%" spacing="2rem">
          <HStack>
            <Button onClick={(e) => (state.view = "new")} leftIcon={<RiAddFill />}>New model</Button>

          </HStack>

          <Stack>
            {models.map((name) => (
              <Model
                onClick={(e) => {state.view = "show_blueprint", state.name ={name}}}
                name={name}
                key={name}
                onDelete={(e) =>
                  CLIENT.models[name].delete().then((resp) => {
                    _state.refresh = new Date();
                  })
                }
              />
            ))}
          </Stack>
        </Stack>
      );
    case "new":
      return (
        <Flex w="100vw" h="100vh" p="2rem">
          <ModelCreation onClose={(e) => (state.view = "list")} />
        </Flex>
      );
    case "show_blueprint":
      console.log("Models in details::::")
      return (
        <Flex w="100vw" h="100vh" p="2rem">
          <ModelDetails onClose={(e) => (state.view = "list")} name={Object.values(state.name)} />
        </Flex>

      );
      

    default:
      break;
  }
}
