import { Box, Button, Chip, Divider, IconButton } from "@mui/material";
import { Trans } from "react-i18next";
import { styles, getMaturityLevelColors } from "@styles";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import InfoItem from "@common/InfoItem";
import formatDate from "@utils/formatDate";
import { t } from "i18next";
import RichEditor from "@common/rich-editor/RichEditor";
import Title from "@common/Title";
import { useServiceContext } from "@providers/ServiceProvider";
import { useQuery } from "@utils/useQuery";
import { TQueryFunction } from "@types";
import { useParams } from "react-router";
import ArchiveRoundedIcon from "@mui/icons-material/ArchiveRounded";
import PublishedWithChangesRoundedIcon from "@mui/icons-material/PublishedWithChangesRounded";
import { toast } from "react-toastify";
interface IAssessmentKitSectionAuthorInfo {
  data: any;
  query: TQueryFunction;
}
const AssessmentKitSectionGeneralInfo = (props: IAssessmentKitSectionAuthorInfo) => {
  const { data, query } = props;
  const { is_active, is_expert = true } = data || {};
  const { assessmentKitId } = useParams();
  const { service } = useServiceContext();
  const publishQuery = useQuery({
    service: (args = { id: assessmentKitId }, config) =>
      service.publishAssessmentKit(args, config),
    runOnMount: false,
    toastError: true,
  });
  const unPublishQuery = useQuery({
    service: (args = { id: assessmentKitId }, config) =>
      service.unPublishAssessmentKit(args, config),
    runOnMount: false,
    toastError: true,
  });
  const publishAssessmentKit = async () => {
    try {
      const res = await publishQuery.query();
      res.message && toast.success(res.message);
      query();
    } catch (e) {}
  };
  const unPublishAssessmentKit = async () => {
    try {
      const res = await unPublishQuery.query();
      res.message && toast.success(res.message);
      query();
    } catch (e) {}
  };
  return (
    <Grid container spacing={4}>
      <Grid item xs={12} md={7}>
        <Title size="small" sx={{ opacity: 0.9 }}>
          <Trans i18nKey="about" />
        </Title>
        <Box sx={{ background: "white", borderRadius: 2, p: 2.5, mt: 1 }}>
          <RichEditor content={data.about} />
        </Box>
      </Grid>
      <Grid item xs={12} md={5}>
        <Title size="small" sx={{ opacity: 0.9 }}>
          <Trans i18nKey="detail" />
        </Title>
        <Box
          sx={{
            mt: 1,
            p: 2.5,
            borderRadius: 2,
            background: "white",
          }}
        >
          {data.summary && (
            <Typography sx={{ p: 1 }} variant="body2">
              {data.summary}
            </Typography>
          )}
          <Box my={1.5}>
            <InfoItem
              bg="white"
              info={{
                action: is_expert ? (
                  is_active ? (
                    <IconButton
                      color="primary"
                      title="Unpublish"
                      onClick={unPublishAssessmentKit}
                    >
                      <ArchiveRoundedIcon />
                    </IconButton>
                  ) : (
                    <IconButton
                      color="primary"
                      title="Publish"
                      onClick={publishAssessmentKit}
                    >
                      <PublishedWithChangesRoundedIcon />
                    </IconButton>
                  )
                ) : undefined,
                item: is_active ? (
                  <Chip
                    component="span"
                    label={<Trans i18nKey="published" />}
                    color="success"
                    size="small"
                  />
                ) : (
                  <Chip
                    component="span"
                    label={<Trans i18nKey="unPublished" />}
                    size="small"
                  />
                ),
                title: "Publish status",
              }}
            />
          </Box>
          {data.assessmentkitInfos.map((info: any, index: number) => {
            return (
              <Box my={1.5} key={index}>
                <InfoItem
                  bg="white"
                  info={{
                    ...info,
                    type: info.title === "Subjects" ? "array" : info.type,
                  }}
                />
              </Box>
            );
          })}
          {data?.creation_date && (
            <Box my={1.5}>
              <InfoItem
                bg="white"
                info={{
                  item: formatDate(data?.creation_date),
                  title: t("creationDate"),
                }}
              />
            </Box>
          )}
          {data?.last_update && (
            <Box my={1.5}>
              <InfoItem
                bg="white"
                info={{
                  item: formatDate(data?.last_update),
                  title: t("lastUpdated"),
                }}
              />
            </Box>
          )}
          {data?.maturity_levels?.list[0] && (
            <Box my={1.5}>
              <InfoItem
                bg="white"
                info={{
                  item: (
                    <AssessmentKitMaturityLevels
                      maturity_levels={data?.maturity_levels}
                    />
                  ),
                  title: t("maturityLevels"),
                }}
              />
            </Box>
          )}
        </Box>
      </Grid>
    </Grid>
  );
};
const AssessmentKitMaturityLevels = (props: any) => {
  const { maturity_levels } = props;
  const { list, maturity_level_number } = maturity_levels;
  const colorPallet = getMaturityLevelColors(maturity_level_number);
  return (
    <Box>
      <Grid
        container
        spacing={1}
        columns={maturity_level_number}
        direction="row"
        alignItems="center"
      >
        {list.map((item: any, index: number) => {
          const colorCode = colorPallet[item?.value];
           return (
             <Box
               sx={{
                 borderBottom: `2px solid ${colorCode}`,
                 px: "8px",
                 py: "2px",
                 textAlign: "center",
               }}
             >
               <Typography
                 fontSize="12px"
                 fontWeight="bold"
               >
                 {item.title}
               </Typography>
            </Box>
          );
        })}
      </Grid>
    </Box>
  );
};
export default AssessmentKitSectionGeneralInfo;