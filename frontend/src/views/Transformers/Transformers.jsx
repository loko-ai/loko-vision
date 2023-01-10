import { Button, Flex, HStack, Stack } from "@chakra-ui/react";
import { useCompositeState } from "ds4biz-core";
import { useContext } from "react";
import { CLIENT, StateContext } from "../../config/constants";
import { Transformer } from "./Transformer";
import { TransformCreation } from "./TransformerCreation";
import { RiAddFill } from 'react-icons/ri';
import { TransformerDetails } from "./TransformerDetails";


export function Transformers({ transformers }) {
  const state = useCompositeState({ view: "list" });
  const _state = useContext(StateContext);
  switch (state.view) {
    case "list":
      return (
        <Stack w="100%" h="100%" spacing="2rem">
          <HStack>
            <Button onClick={(e) => (state.view = "new")} leftIcon={<RiAddFill />}>
              New transformer
            </Button>
          </HStack>

          <Stack>
            {transformers.map((name) => (
              <Transformer
              onClick={(e) => {state.view = "show_blueprint", state.name ={name}}}
              name={name}
                key={name}
                onDelete={(e) =>
                  CLIENT.transformers[name].delete().then((resp) => {
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
          <TransformCreation onClose={(e) => (state.view = "list")} />
        </Flex>
      );
      case "show_blueprint":
        console.log("Transformer in detailssssssss::::")
        return (
          <Flex w="100vw" h="100vh" p="2rem">
            <TransformerDetails onClose={(e) => (state.view = "list")} name={Object.values(state.name)} />
          </Flex>
  
        );

    default:
      break;
  }
}
