<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-select v-model="survey"
                   placeholder="问卷标题"
                   clearable
                   @change="handleSurveyEvent"
                   style="width: 240px">
          <el-option v-for="(item, index) in surveyList" :key="index" :label="item.title"
                     :value="item.id"></el-option>
        </el-select>
        <el-select v-model="question"
                   placeholder="选择问题"
                   clearable
                   style="width: 240px">
          <el-option v-for="(item, index) in questionList" :key="index" :label="item.question_text"
                     :value="item.id"></el-option>
        </el-select>
        <el-input
          v-model="listQuery.search"
          placeholder="输入关键进行搜索"
          style="width: 300px"
          class="filter-item"
          @keyup.native="handleFilter"
        />
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="resetFilter"
        >查询
        </el-button
        >
      </div>
    </el-card>

    <el-table
      v-loading="listLoading"
      :data="
        tableDataList.results.filter(
          (data) =>
            !search || data.title.toLowerCase().includes(search.toLowerCase())
        )
      "
      style="width: 100%; margin-top: 10px"
      highlight-current-row
      row-key="id"
      height="100"
      stripe
      border
      v-el-height-adaptive-table="{ bottomOffset: 50 }"
    >
      <el-table-column label="ID" width="60">
        <template slot-scope="scope">{{ scope.row.id }}</template>
      </el-table-column>
      <el-table-column label="用户id">
        <template slot-scope="scope">{{ scope.row.user_id }}</template>
      </el-table-column>
      <el-table-column label="问卷标题">
        <template slot-scope="scope">{{ scope.row.survey_info.title }}</template>
      </el-table-column>
      <el-table-column label="问题">
        <template slot-scope="scope">{{ scope.row.question_info.question_text }}</template>
      </el-table-column>
      <el-table-column label="答案">
        <template slot-scope="scope">{{ scope.row.answer }}</template>
      </el-table-column>
      <el-table-column label="回答时间">
        <template slot-scope="scope">
          <span>{{ scope.row.response_time }}</span>
        </template>
      </el-table-column>
      <!--      <el-table-column align="center" label="操作">-->
      <!--        <template slot-scope="scope">-->
      <!--          <el-button-->
      <!--            type="primary"-->
      <!--            size="mini"-->
      <!--            icon="el-icon-edit"-->
      <!--            :disabled="!checkPermission(['position_update'])"-->
      <!--            @click="handleEdit(scope)"-->
      <!--          />-->
      <!--          <el-button-->
      <!--            type="success"-->
      <!--            size="mini"-->
      <!--            :disabled="!checkPermission(['position_update'])"-->
      <!--            @click="goToQuestionsPage(scope)">-->
      <!--            录入问题-->
      <!--          </el-button>-->
      <!--          <el-button-->
      <!--            type="info"-->
      <!--            size="mini"-->
      <!--            :disabled="!checkPermission(['position_update'])"-->
      <!--            @click="handleEdit(scope)">-->
      <!--            信息按钮-->
      <!--          </el-button>-->
      <!--          <el-button-->
      <!--            type="danger"-->
      <!--            size="mini"-->
      <!--            icon="el-icon-delete"-->
      <!--            :disabled="!checkPermission(['position_delete'])"-->
      <!--            @click="handleDelete(scope)"-->
      <!--          />-->
      <!--        </template>-->
      <!--      </el-table-column>-->
    </el-table>
    <el-pagination
            v-show="tableDataList.count>0"
            :total="tableDataList.count"
            :page-size.sync="listQuery.page_size"
            :layout="prev,pager,next"
            :current-page.sync="listQuery.page"
            @current-change="getList"
    ></el-pagination>
    <!--    <el-dialog-->
    <!--      :visible.sync="dialogVisible"-->
    <!--      :title="dialogType === 'edit' ? '编辑问卷' : '新增问卷'"-->
    <!--    >-->
    <!--      <el-form-->
    <!--        ref="Form"-->
    <!--        :model="tableData"-->

    <!--        label-width="80px"-->
    <!--        label-position="right"-->
    <!--      >-->
    <!--        <el-form-item label="问卷标题" prop="title">-->
    <!--          <el-input v-model="tableData.title" placeholder="问卷标题"/>-->
    <!--        </el-form-item>-->
    <!--        <el-form-item label="问卷描述" prop="description">-->
    <!--          <el-input v-model="tableData.description" placeholder="问卷描述"/>-->
    <!--        </el-form-item>-->
    <!--        <el-form-item label="开始时间" prop="start_time">-->
    <!--          <el-date-picker v-model="tableData.start_time" placeholder="课时数量" type="datetime"/>-->
    <!--        </el-form-item>-->
    <!--        <el-form-item label="结束时间" prop="expiry_time">-->
    <!--          <el-date-picker v-model="tableData.expiry_time" placeholder="结束时间" type="datetime"/>-->
    <!--        </el-form-item>-->
    <!--      </el-form>-->
    <!--      <span slot="footer">-->
    <!--        <el-button type="danger" @click="dialogVisible = false">取消</el-button>-->
    <!--        <el-button type="primary" @click="confirm('Form')">确认</el-button>-->
    <!--      </span>-->
    <!--    </el-dialog>-->
  </div>
</template>

<script>
import {
  getSurveyList,
} from "@/api/survey";
import {getQuestionsList} from "@/api/questions";
import {getResponsesList, createResponses, updateResponses, deleteResponses} from "@/api/responses";

import {genTree, deepClone} from "@/utils";
import checkPermission from "@/utils/permission";
import {getEnumConfigList} from "@/api/enum_config";

const defaultM = {};
export default {
  data() {
    return {
      tableData: {
        id: "",
        survey: {},
        user_id: "",
        question: {},
        answer: "",
        response_time: "",
        create_time: "",
        update_time: ""
      },
      search: "",
      survey: null,
      surveyList: [],
      question: null,
      questionList: [],
      tableDataList: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      typeOptions: [],
      listQuery: {
        page: 1,
        page_size: 20,
        search: null
      },
      enumConfigQuery: {}
    };
  },
  computed: {},
  created() {
    this.getSurveyList().then(() => {
      this.getQuestions();
      this.getList();
    });
  },
  methods: {
    checkPermission,
    getQuestions(){
      getQuestionsList({survey: this.survey}).then((response) => {
          this.questionList = response.data.results;
        })
    },
    getSurveyList() {
      return new Promise((resolve, reject) => {
        getSurveyList({}).then((response) => {
          this.surveyList = response.data.results;
          if (this.surveyList && this.surveyList.length > 0) {
            this.survey = this.surveyList[0].id;
          }
          resolve()
        })
      })
    },
    getList() {
      this.listLoading = true;
      this.listQuery.survey = this.survey;
      this.listQuery.question = this.question;
      getResponsesList(this.listQuery).then((response) => {
        this.tableDataList = response.data;
        this.tableData = response.data;
        this.listLoading = false;
      });
    },
    resetFilter() {
      this.getList();
    },
    handleSurveyEvent(){
      this.getQuestions();
    },
    handleFilter() {
      const newData = this.tableDataList.filter(
        (data) =>
          !this.search ||
          data.title.toLowerCase().includes(this.search.toLowerCase())
      );
      this.tableData = genTree(newData);
    },
    handleAdd() {
      this.tableData = Object.assign({}, defaultM);
      this.dialogType = "new";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
    handleEdit(scope) {
      this.tableData = Object.assign({}, scope.row); // copy obj
      this.dialogType = "edit";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
    handleDelete(scope) {
      this.$confirm("确认删除?", "警告", {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "error",
      })
        .then(async () => {
          await deleteResponses(scope.row.id);
          this.getList();
          this.$message({
            type: "success",
            message: "成功删除!",
          });
        })
        .catch((err) => {
          console.error(err);
        });
    },
    goToQuestionsPage(scope) {
      this.$router.push({name: 'questions', params: scope});
    },
    async confirm(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const isEdit = this.dialogType === "edit";
          if (isEdit) {
            updateResponses(this.tableData.id, this.tableData).then(() => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success",
              });
            });
          } else {
            createResponses(this.tableData).then((res) => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "新增成功",
                type: "success",
              });
            });
          }
        } else {
          return false;
        }
      });
    },
  },
};
</script>
