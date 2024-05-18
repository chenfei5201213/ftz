<template>
  <div class="app-container">
    <el-card>
      <div>
<!--       <el-select v-model="course" placeholder="请选择" clearable>-->
<!--          <el-option-->
<!--            v-for="item in courseList"-->
<!--            :key="item.id"-->
<!--            :label="`【${item.id}】- ${item.title} (${item.type})`"-->
<!--            :value="item.id">-->
<!--            &lt;!&ndash;            <span style="float: right; color: #8492a6; font-size: 13px">{{ item.value }}</span>&ndash;&gt;-->
<!--          </el-option>-->
<!--        </el-select>-->
<!--        <el-select v-model="question"-->
<!--                   placeholder="选择问题"-->
<!--                   clearable-->
<!--                   style="width: 240px">-->
<!--          <el-option v-for="(item, index) in questionList" :key="index" :label="item.question_text"-->
<!--                     :value="item.id"></el-option>-->
<!--        </el-select>-->
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
      <el-table-column label="期课Id">
        <template slot-scope="scope">{{ scope.row.term_course }}</template>
      </el-table-column>
      <el-table-column label="用户id">
        <template slot-scope="scope">{{ scope.row.user }}</template>
      </el-table-column>
      <el-table-column label="加课时间">
        <template slot-scope="scope">{{ scope.row.create_time }}</template>
      </el-table-column>
      <el-table-column label="过期时间">
        <template slot-scope="scope">{{ scope.row.term_course_info.course_end }}</template>
      </el-table-column>
      <el-table-column label="状态">
        <template slot-scope="scope">{{ scope.row.study_status }}</template>
      </el-table-column>


    </el-table>
    <el-pagination
            v-show="tableDataList.count>0"
            :total="tableDataList.count"
            :page-size.sync="listQuery.page_size"
            :layout="prev,pager,next"
            :current-page.sync="listQuery.page"
            @current-change="getList"
    ></el-pagination>

  </div>
</template>

<script>
import {
  getCourseList,
} from "@/api/course";
import {
  getScUserById,
  getScUserList,
  createScUser,
  deleteScUser,
  updateScUser
} from "@/api/sc_user";

import {genTree, deepClone} from "@/utils";
import checkPermission from "@/utils/permission";
import {getEnumConfigList} from "@/api/enum_config";

const defaultM = {};
export default {
  data() {
    return {
      tableData: {
        id: "",
        course: {},
        user_id: "",
        question: {},
        answer: "",
        response_time: "",
        create_time: "",
        update_time: ""
      },
      search: "",
      course: null,
      CourseList: [],
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
    this.getCourseList().then(() => {
      this.getScUser();
      this.getList();
    });
  },
  methods: {
    checkPermission,
    getScUser(){
      getScUserList({survey: this.survey}).then((response) => {
          this.questionList = response.data.results;
        })
    },
    getCourseList() {
      return new Promise((resolve, reject) => {
        getCourseList({}).then((response) => {
          this.CourseList = response.data.results;
          if (this.CourseList && this.CourseList.length > 0) {
            this.course = this.CourseList[0].id;
          }
          resolve()
        })
      })
    },
    getList() {
      this.listLoading = true;
      this.listQuery.course = this.course;
      getScUserList(this.listQuery).then((response) => {
        this.tableDataList = response.data;
        this.listLoading = false;
      });
    },
    resetFilter() {
      this.getList();
    },
    handleSurveyEvent(){
      this.getScUser();
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
          await deleteScUser(scope.row.id);
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
            updateScUser(this.tableData.id, this.tableData).then(() => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success",
              });
            });
          } else {
            createScUser(this.tableData).then((res) => {
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
