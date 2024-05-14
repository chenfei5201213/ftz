<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增题目</el-button>
        <el-select v-model="survey"
                   placeholder="问卷标题"
                   clearable
                   style="width: 120px">
          <el-option v-for="(item, index) in surveyList" :key="index" :label="item.title"
                     :value="item.id"></el-option>
        </el-select>
        <el-input
          v-model="listQuery.search"
          placeholder="输入问卷标题进行搜索"
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
        tableDataList.filter(
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
      <el-table-column label="问题类型">
        <template slot-scope="scope">{{ scope.row.question_type }}</template>
      </el-table-column>
      <el-table-column label="问题内容">
        <template slot-scope="scope">{{ scope.row.question_text }}</template>
      </el-table-column>
      <el-table-column label="问题选项">
        <template slot-scope="scope">{{ scope.row.options }}</template>
      </el-table-column>
      <el-table-column label="创建日期">
        <template slot-scope="scope">
          <span>{{ scope.row.create_time }}</span>
        </template>
      </el-table-column>
      <el-table-column label="更新时间">
        <template slot-scope="scope">
          <span>{{ scope.row.update_time }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作">
        <template slot-scope="scope">
          <el-button
            type="primary"
            size="mini"
            icon="el-icon-edit"
            :disabled="!checkPermission(['position_update'])"
            @click="handleEdit(scope)"
          />
          <el-button
            type="danger"
            size="mini"
            icon="el-icon-delete"
            :disabled="!checkPermission(['position_delete'])"
            @click="handleDelete(scope)"
          />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑问题' : '新增问题'"
    >
      <el-form
        ref="Form"
        :model="tableData"

        label-width="80px"
        label-position="right"
      >
        <el-form-item label="问题类型" prop="title">
          <el-input v-model="tableData.question_type" placeholder="问题类型"/>
        </el-form-item>
        <el-form-item label="问题内容" prop="question_text">
          <el-input v-model="tableData.question_text" placeholder="问题内容"/>
        </el-form-item>
        <el-form-item label="问题选项" prop="options">
          <el-input v-model="tableData.options" placeholder="问题选项"/>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button type="danger" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  getSurveyList,
} from "@/api/survey";
import {
  getQuestionsList,
  getQuestionsById,
  createQuestions,
  updateQuestions,
  deleteQuestions
} from "@/api/questions";
import {genTree, deepClone} from "@/utils";
import checkPermission from "@/utils/permission";
import {getEnumConfigList} from "@/api/enum_config";
import {getCourseList} from "@/api/course";

const defaultM = {
};
export default {
  data() {
    return {
      tableData: {
        id: "",
        question_type: "",
        question_text: "",
        options: "",
        survey: "",
        create_time: "",
        update_time: ""
      },
      search: "",
      tableDataList: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      surveyList: [],
      survey: null,
      listQuery: {
        page: 1,
        page_size: 20,
        search: null
      },
      enumConfigQuery: {
        module: 'course',
        service: 'type'
      }
    };
  },
  computed: {},
  created() {
    this.getSurveyList().then(()=>{
      this.getList();
    });

  },
  methods: {
    checkPermission,
    getSurveyList() {
      return new Promise((resolve, reject) => {
        getSurveyList({}).then((response) => {
          this.surveyList = response.data;
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
      getQuestionsList(this.listQuery).then((response) => {
        this.tableDataList = response.data;
        this.tableData = response.data;
        this.listLoading = false;
      });
    },
    resetFilter() {
      this.getList();
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
      this.tableData.survey = this.survey;
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
          await deleteQuestions(scope.row.id);
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
            updateQuestions(this.tableData.id, this.tableData).then(() => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success",
              });
            });
          } else {
            createQuestions(this.tableData).then((res) => {
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
