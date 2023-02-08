import {
  Avatar,
  AvatarGroup,
  Box,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Divider,
  Link as MLink,
} from "@mui/material";
import EditRoundedIcon from "@mui/icons-material/EditRounded";
import { Link } from "react-router-dom";
import { styles } from "../../config/styles";
import useMenu from "../../utils/useMenu";
import MoreActions from "../shared/MoreActions";
import { useQueryDataContext } from "../shared/QueryData";
import { useServiceContext } from "../../providers/ServiceProvider";
import { useQuery } from "../../utils/useQuery";
import { Trans } from "react-i18next";
import useDialog from "../../utils/useDialog";
import ExpertGroupCEFormDialog from "./ExpertGroupCEFormDialog";
import { useAuthContext } from "../../providers/AuthProvider";

interface IExpertGroupsItemProps {
  data: any;
  disableActions?: boolean;
}

const ExpertGroupsItem = (props: IExpertGroupsItemProps) => {
  const { data, disableActions = false } = props;
  const {
    id,
    name,
    picture,
    bio = "",
    website,
    about = "",
    users = [],
    number_of_profiles,
  } = data || {};

  return (
    <Box>
      <Card>
        <CardHeader
          titleTypographyProps={{
            component: Link,
            to: `${id}`,
            sx: { textDecoration: "none" },
          }}
          avatar={
            <Avatar
              component={Link}
              to={`${id}`}
              sx={(() => {
                return {
                  bgcolor: (t) => t.palette.grey[800],
                  textDecoration: "none",
                };
              })()}
              src={picture}
            >
              {name?.[0]?.toUpperCase()}
            </Avatar>
          }
          action={!disableActions && <Actions expertGroup={data} />}
          title={
            <Box component={"b"} color="GrayText" fontSize=".95rem">
              {name}
            </Box>
          }
          subheader={
            <Box sx={{ ...styles.centerV, textTransform: "lowercase" }}>
              {number_of_profiles} <Trans i18nKey="profiles" />
            </Box>
          }
        />
        <CardContent
          sx={{
            height: "48px",
            padding: 0,
            margin: 2,
            overflow: "hidden",
            textOverflow: "ellipsis",
            maxWidth: "calc(100% - 16px)",
            whiteSpace: "pre-wrap",
            display: "-webkit-box",
            "-webkit-box-orient": "vertical",
            "-webkit-line-clamp": "2",
          }}
        >
          {bio}
        </CardContent>
        <Divider sx={{ mx: 2 }} />
        <CardActions disableSpacing>
          <AvatarGroup
            total={users.length}
            max={5}
            sx={{ mx: 0.5 }}
            slotProps={{
              additionalAvatar: {
                sx: { width: 28, height: 28, fontSize: ".75rem" },
              },
            }}
          >
            {users.map((user: any) => {
              return (
                <Avatar
                  key={user.id}
                  sx={{ width: 28, height: 28, fontSize: ".8rem" }}
                  alt={user.display_name}
                  title={user.display_name}
                  src="/"
                />
              );
            })}
          </AvatarGroup>
        </CardActions>
      </Card>
    </Box>
  );
};

const Actions = (props: any) => {
  const { expertGroup } = props;
  const { query: fetchExpertGroups } = useQueryDataContext();
  const { userInfo } = useAuthContext();
  const { service } = useServiceContext();
  const { id } = expertGroup;
  const { query: fetchExpertGroup, loading } = useQuery({
    service: (args = { id }, config) =>
      service.fetchUserExpertGroup(args, config),
    runOnMount: false,
  });
  const dialogProps = useDialog();
  const isOwner = expertGroup?.owner?.id === userInfo.id;

  const openEditDialog = async (e: any) => {
    const data = await fetchExpertGroup();
    dialogProps.openDialog({
      data,
      type: "update",
    });
  };

  return isOwner ? (
    <>
      <MoreActions
        {...useMenu()}
        boxProps={{ ml: 0.2 }}
        loading={loading}
        items={[
          {
            icon: <EditRoundedIcon fontSize="small" />,
            text: <Trans i18nKey="edit" />,
            onClick: openEditDialog,
          },
        ]}
      />
      <ExpertGroupCEFormDialog
        {...dialogProps}
        onSubmitForm={fetchExpertGroups}
      />
    </>
  ) : null;
};

export default ExpertGroupsItem;
