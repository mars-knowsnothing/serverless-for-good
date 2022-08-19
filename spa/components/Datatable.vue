<template>
  <el-tabs v-model="activeTabName" class="demo-tabs">
    <el-tab-pane label="Rule" name="rules">
      <el-row :gutter="20">
        <el-col :span="2">
          <el-button :offset="10" @click="authDisplay = true;" style="width: 100px;">Auth</el-button>
        </el-col>
        <el-col v-if="apiKey" :span="2">
          <el-button :offset="10" style="width: 100px;" @click="createRuleDialogDisplay = true;">Create</el-button>
        </el-col>
        <el-col :span="2">
          <el-tag v-if="apiKey">API Key - {{ apiKey }}</el-tag>
        </el-col>
      </el-row>
      <el-table :data="tableData" style="width: 100%">
        <el-table-column fixed prop="ruleName" label="RuleName" />
        <el-table-column prop="accountId" label="AccountId" />
        <el-table-column prop="action" label="Action" />
        <el-table-column prop="filters" label="Filters">
          <template #default="scope">
            <el-tag v-for="(value, propertyName) in scope.row.filters">{{ propertyName }} = {{ value }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="scheduleExpression" label="ScheduleExpression" />
        <el-table-column prop="updatedAt" label="UpdatedAt" />
        <el-table-column fixed="right" label="Operations">
          <template #default="scope">
            <el-button link type="primary" @click="onClickCheck(scope.$index, scope.row)">Logs</el-button>
            <el-button link type="danger" @click="onClickDelete(scope.$index, scope.row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-dialog v-model="authDisplay" title="Auth Info">
        <el-form>
          <el-form-item label="API Key" :label-width="dialogWidth">
            <el-input v-model="apiKey" placeholder="Please Enter API Key" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="authDisplay = false">Cancel</el-button>
            <el-button type="primary" @click="onSaveAPIKey">Confirm</el-button>
          </span>
        </template>
      </el-dialog>
      <el-dialog v-model="createRuleDialogDisplay" title="Auth Info">
        <el-form>
          <el-form :model="createRulePayload" label-width="120px">
            <el-form-item label="Rule Name">
              <el-input v-model="createRulePayload.ruleName" />
            </el-form-item>
            <el-form-item label="Account Id">
              <el-input v-model="createRulePayload.accountId" />
            </el-form-item>
            <el-form-item label="Action">
              <el-select v-model="createRulePayload.action" placeholder="please select action">
                <el-option label="Start Instances" value="start_instances" />
                <el-option label="Stop Instances" value="stop_instances" />
              </el-select>
            </el-form-item>
            <el-form-item label="Filters">
              <el-input v-model="filterString" type="textarea" />
            </el-form-item>
            <el-form-item label="ScheduleExpression">
              <el-input v-model="createRulePayload.scheduleExpression" />
            </el-form-item>
          </el-form>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="createRuleDialogDisplay = false">Cancel</el-button>
            <el-button type="primary" @click="onSubmitCreate">Confirm</el-button>
          </span>
        </template>
      </el-dialog>
    </el-tab-pane>
    <el-tab-pane label="Log" name="logs">
      <el-table :data="logTableData" style="width: 100%">
        <el-table-column fixed prop="eventId" label="EventId" />
        <el-table-column prop="updatedAt" label="TimeStamp" />
        <el-table-column prop="params.action" label="Action" />
        <el-table-column label="Filters">
          <template #default="scope">
            <el-tag v-for="(value, propertyName) in scope.row.params.filters">{{ propertyName }} = {{ value }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Targets">
          <template #default="scope">
          <div v-if="scope.row.response.StoppingInstances">
            <p v-for="instance in scope.row.response.StoppingInstances">{{instance.InstanceId}}</p>
          </div>
          <div v-if="scope.row.response.StartingInstances">
            <p v-for="instance in scope.row.response.StartingInstances">{{instance.InstanceId}}</p>
          </div>
          </template>
        </el-table-column>

      </el-table>
    </el-tab-pane>
  </el-tabs>

</template>

<script lang="tsx" setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Load Rules
const url = "https://g8bfit35p3.execute-api.ap-southeast-1.amazonaws.com/dev/resources/schedule/rules";
const { data: resp, pending, refresh, error } = await useFetch(url);
console.log(resp.value)
let tableData: ScheduleRule[] = reactive(resp.value.data);

// Load Logs
const log_url = "https://g8bfit35p3.execute-api.ap-southeast-1.amazonaws.com/dev/resources/schedule/logs";
const { data: log_resp } = await useFetch(log_url);
console.log(log_resp.value)
let logTableData = reactive(log_resp.value.data);

const authorized = ref(false);
const createRuleDialogDisplay = ref(false)
const authDisplay = ref(false)

const activeTabName = ref('rules')
const filterString = ref("");
const createRulePayload = reactive({
  ruleName: "",
  action: "",
  accountId: "",
  scheduleExpression: "",
  targetArn: "arn:aws:sqs:ap-southeast-1:592336536196:sqs_dev_ec2_state_change",
  targetId: "sqs_ec2_state_change",
  filters: {},
  desiredState: {}
});

const dialogWidth = '140px'
const apiKey = ref('');
interface ScheduleRule {
  desiredState: Map<string, string>;
  targetId: string;
  action: string;
  accountId: string;
  scheduleExpression: string;
  updatedAt: Date;
  targetArn: string;
  ruleId: string;
  ruleName: string;
  filters: Map<string, string>;
}


const apiKeyCookie = useCookie("apiKeyCookie");
if (apiKeyCookie.value) {
  apiKey.value = apiKeyCookie.value
}
const onSaveAPIKey = () => {
  apiKeyCookie.value = apiKey.value
  console.log(apiKeyCookie.value)
  authorized.value = true;
  authDisplay.value = false;
}
const onClickCheck = async (index, row) => {
  console.log(row.ruleId)
}
const onDelete = async (index, row) => {
  console.log(row);
  const { data: resp } = await useFetch(
    "https://g8bfit35p3.execute-api.ap-southeast-1.amazonaws.com/dev/resources/schedule/rules/" + row.ruleId,
    {
      method: "delete",
      headers: {
        'x-api-key': apiKeyCookie.value
      }
    }
  )
  console.log(resp.value);
};

const onClickDelete = (index, row) => {
  ElMessageBox.confirm(
    'The schedule rule will be permanently deleted. Continue?',
    'Warning',
    {
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  ).then(() => {
    onDelete(index, row)
    ElMessage({
      type: 'success',
      message: 'Delete completed',
    })
  }).catch(() => {
    ElMessage({
      type: 'info',
      message: 'Delete canceled',
    })
  })
}


const onSubmitCreate = async () => {
  if (createRulePayload.action == "start_instances") {
    createRulePayload.desiredState = {
      name: "running"
    }
  } else if (createRulePayload.action == "stop_instances") {
    createRulePayload.desiredState = {
      name: "stopped"
    }
  }
  const filterList = filterString.value.split(",")
  for (var i in filterList) {
    var f = filterList[i].split("=")
    createRulePayload.filters[f[0]] = f[1]
  }
  console.log(createRulePayload)
  await useFetch("https://g8bfit35p3.execute-api.ap-southeast-1.amazonaws.com/dev/resources/schedule/rules", {
    method: "post",
    body: createRulePayload,
    headers: {
      'x-api-key': apiKeyCookie.value
    }
  }).then(
    res => {
      const error = res.error.value
      if (error) {
        console.log(error)
        // dealing error
        ElMessage.error('Failed to create rule, please check the API Key')
      } else {
        location.reload()
      }
    }, error => {
      console.log('exception...')
      console.log(error)
    }
  );
  createRuleDialogDisplay.value = false;

}
</script>